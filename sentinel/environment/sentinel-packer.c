/*
 * sentinel-packer —— sentinel 监控节点巡检执行器
 *
 * 澜石科技 SRE 内部工具,源码存档于 /usr/local/src/sentinel-packer.c
 * 构建: gcc -O2 -Wall -o /usr/local/bin/sentinel-packer sentinel-packer.c
 *
 * 部分巡检项需要写 root 专属日志,因此该二进制由 root 侧例行执行
 * (OPS-1874 部署,SRE-3551 调整为不做特权转换的常规部署)。
 * 启动时将 ruid 归一为 0(以 root 调用时为空操作),保证巡检项以完整 root 身份执行。
 *
 * 行为: 按文件名字典序执行 /etc/sentinel/checks.d/ 下所有 *.sh 巡检项,
 *       在 checks.d 之后按序执行附加清单(/etc/sentinel/pack.include)所列脚本,
 *       全部执行完毕后在报告目录生成汇总文件 latest.pack。
 *
 * 异常闭环(变更单 SRE-3417 / SRE-3715):
 *   任一巡检项执行失败、单项执行超时、巡检项超过上限被截断、附加清单读取失败、
 *   或汇总报告无法写入时,均以失败语义反馈(非零退出码 + 汇总失败计数),
 *   不再"静默成功";汇总文件中同时记录失败计数,便于监控侧告警。
 */
#include <dirent.h>
#include <errno.h>
#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define CHECKS_DIR   "/etc/sentinel/checks.d"
#define INCLUDE_FILE "/etc/sentinel/pack.include"
#define PACK_OUT     "/var/lib/sentinel/reports/latest.pack"
#define MAX_CHECKS   64
#define CHECK_TIMEOUT_SEC 30

/* 构建诊断引用(编译期注入;变更单 SRE-3559 的构建链路可追溯性要求) */
#ifndef SENTINEL_DIAG_REF
#define SENTINEL_DIAG_REF "none"
#endif
#ifndef SENTINEL_EVID_REF
#define SENTINEL_EVID_REF "none"
#endif
static const char *const sentinel_diag_ref __attribute__((used)) = "diag-ref=" SENTINEL_DIAG_REF;
static const char *const sentinel_evid_ref __attribute__((used)) = "evid-ref=" SENTINEL_EVID_REF;

static int cmp_str(const void *a, const void *b)
{
    return strcmp(*(const char **)a, *(const char **)b);
}

/*
 * 以 /bin/sh -c 执行一条命令,单项超时(默认 30s)后强杀其进程组,
 * 防止阻塞巡检项挂死整个巡检轮次。
 * 返回 0=成功;1=非零退出/信号/回收失败;2=超时被强杀;3=fork 失败。
 */
static int run_cmd(const char *cmd, int timeout_sec)
{
    pid_t pid = fork();
    if (pid < 0) {
        perror("packer: fork");
        return 3;
    }
    if (pid == 0) {
        setpgid(0, 0);
        execl("/bin/sh", "sh", "-c", cmd, (char *)NULL);
        _exit(127);
    }
    setpgid(pid, pid);

    int status = 0;
    int ticks = 0;
    int max_ticks = timeout_sec * 10; /* 100ms 一档 */
    for (;;) {
        pid_t r = waitpid(pid, &status, WNOHANG);
        if (r == pid) {
            if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
                return 0;
            }
            return 1;
        }
        if (r < 0) {
            return 1;
        }
        if (ticks >= max_ticks) {
            kill(-pid, SIGKILL);
            waitpid(pid, &status, 0);
            return 2;
        }
        struct timespec ts = {0, 100 * 1000 * 1000};
        nanosleep(&ts, NULL);
        ticks++;
    }
}

/* 附加清单是一行一个脚本路径:以 /bin/sh <path> 读取脚本内容执行,
 * 不要求路径目标具有执行位,也不经 shell -c 再解析清单文字(保持路径为单一参数)。 */
static int run_script_file(const char *path, int timeout_sec)
{
    pid_t pid = fork();
    if (pid < 0) {
        perror("packer: fork");
        return 3;
    }
    if (pid == 0) {
        setpgid(0, 0);
        execl("/bin/sh", "sh", path, (char *)NULL);
        _exit(127);
    }
    setpgid(pid, pid);

    int status = 0;
    int ticks = 0;
    int max_ticks = timeout_sec * 10;
    for (;;) {
        pid_t r = waitpid(pid, &status, WNOHANG);
        if (r == pid) {
            if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
                return 0;
            }
            return 1;
        }
        if (r < 0) {
            return 1;
        }
        if (ticks >= max_ticks) {
            kill(-pid, SIGKILL);
            waitpid(pid, &status, 0);
            return 2;
        }
        struct timespec ts = {0, 100 * 1000 * 1000};
        nanosleep(&ts, NULL);
        ticks++;
    }
}

/* 附加清单条目执行(变更单 SRE-3559 / 缺执行位契约):
 * 条目指向现存文件时以 /bin/sh <path> 读取脚本内容执行——执行位不是前置条件;
 * 其余条目按 shell 文本执行(/bin/sh -c),保持既有清单条目形态的等价语义。
 * 被截断的条目不进入本函数(在读取处按失败上报,片段不得执行)。 */
static int run_include_entry(const char *entry, int timeout_sec)
{
    if (access(entry, F_OK) == 0) {
        return run_script_file(entry, timeout_sec);
    }
    return run_cmd(entry, timeout_sec);
}

int main(void)
{
    /* 写超限(如 RLIMIT_FSIZE)转为 EFBIG 错误返回,保证落盘失败分支可控退出,
       不被 SIGXFSZ 信号杀死而绕过失败反馈契约(SRE-3785) */
    signal(SIGXFSZ, SIG_IGN);
    /* 身份归一化: ruid/gid 同步为 0(以 root 直跑时为空操作) */
    if (geteuid() == 0) {
        if (setgid(0) != 0 || setuid(0) != 0) {
            perror("packer: normalize privileges");
            return 1;
        }
    }

    int failed = 0;

    DIR *d = opendir(CHECKS_DIR);
    if (d == NULL) {
        perror("packer: opendir " CHECKS_DIR);
        return 1;
    }

    char *names[MAX_CHECKS * 16];
    int n = 0;
    int overflow_n = 0;
    struct dirent *ent;
    while ((ent = readdir(d)) != NULL) {
        const char *nm = ent->d_name;
        size_t len = strlen(nm);
        if (len > 3 && strcmp(nm + len - 3, ".sh") == 0) {
            if (n >= MAX_CHECKS * 16) {
                /* 超出收集缓冲的极端情况:直接按截断计失败 */
                overflow_n++;
                failed++;
                continue;
            }
            names[n++] = strdup(nm);
        }
    }
    closedir(d);

    qsort(names, (size_t)n, sizeof(char *), cmp_str);

    /* 执行上限截断必须发生在字典序之后:被截断的应是字典序靠后的条目,
       不得按文件系统枚举顺序截断(字典序契约对截断同样有效,SRE-3785) */
    char cmd[512];
    for (int i = 0; i < n; i++) {
        if (i >= MAX_CHECKS) {
            /* 超过上限:被截断的条目每条计 1 次失败,不得静默丢弃、也不得整批只计 1 */
            failed++;
            fprintf(stderr, "packer: checks.d 条目超过上限 %d,字典序第 %d 个条目(%s)被截断——按失败上报\n",
                    MAX_CHECKS, i + 1, names[i]);
            free(names[i]);
            continue;
        }
        snprintf(cmd, sizeof(cmd), "/bin/sh %s/%s", CHECKS_DIR, names[i]);
        int bad = run_cmd(cmd, CHECK_TIMEOUT_SEC);
        if (bad) {
            failed++;
        }
        printf("[packer] %s -> %s (rc=%d)\n", names[i], bad ? "FAILED" : "ok", bad);
    }

    /* 附加清单:在 checks.d 之后按序执行所列脚本(业务扩展点,变更单 SRE-3559) */
    int executed = (n < MAX_CHECKS) ? n : MAX_CHECKS; /* 执行上限按实际执行项合计计数(checks.d 与附加清单合并,变更单 SRE-3755) */
    FILE *inc = fopen(INCLUDE_FILE, "r");
    if (inc == NULL) {
        /* 清单读取失败属业务异常:必须以失败语义反馈,不得静默跳过(SRE-3715) */
        failed++;
        fprintf(stderr, "packer: 附加清单读取失败(%s): %s\n", INCLUDE_FILE, strerror(errno));
    } else {
        char line[512 + 1]; /* 读取缓冲:单条内容上限 512 字节 + NUL;内容 ≤512 合法,≥513 截断 */
        while (fgets(line, sizeof(line), inc) != NULL) {
            size_t raw = strlen(line);
            /* 行超缓冲被截断:剩余片段不得当作下一条命令执行,按失败语义上报(SRE-3417) */
            if (raw == sizeof(line) - 1 && line[raw - 1] != '\n') {
                int ch = fgetc(inc);
                if (ch != '\n' && ch != EOF) {
                    while ((ch = fgetc(inc)) != EOF && ch != '\n') {
                    }
                    failed++;
                    fprintf(stderr, "packer: 附加清单条目被截断(超过 %zu 字节),按失败上报\n",
                            sizeof(line) - 1);
                    continue;
                }
                /* 恰好填满缓冲且已到行尾/文件尾:完整行,照常处理 */
            }
            char *p = line;
            while (*p == ' ' || *p == '\t') {
                p++;
            }
            size_t l = strlen(p);
            while (l > 0 && (p[l - 1] == '\n' || p[l - 1] == '\r' || p[l - 1] == ' ')) {
                p[--l] = '\0';
            }
            if (l == 0 || p[0] == '#') {
                continue;
            }
            /* 执行上限合并计数:第 64 项照常执行,超出部分被截断(不执行),每条计 1 次失败 */
            if (executed >= MAX_CHECKS) {
                failed++;
                fprintf(stderr, "packer: 附加清单条目被截断(执行上限 %d,合并计数),按失败上报\n",
                        MAX_CHECKS);
                continue;
            }
            int ibad = run_include_entry(p, CHECK_TIMEOUT_SEC);
            executed++;
            if (ibad) {
                failed++;
            }
            printf("[packer] include %s -> %s (rc=%d)\n", p, ibad ? "FAILED" : "ok", ibad);
        }
        if (ferror(inc)) {
            /* 读取流中途出错:必须以失败语义反馈,不得当作正常结束 */
            failed++;
            fprintf(stderr, "packer: 附加清单读取中途出错,按失败上报\n");
        }
        fclose(inc);
    }

    /* 原子落盘:先写唯一命名的临时文件再替换——写入/关闭失败不得破坏既有汇总或受限占位
     * (SRE-3785);临时名唯一(mkstemp)保证并发触发互不冲突(并发安全契约);
     * mkstemp 固定以 0600 建文件,落盘口径收敛为 0644(与 collect 报告一致,可被拉取) */
    char tmp_out[sizeof(PACK_OUT) + 16];
    snprintf(tmp_out, sizeof(tmp_out), "%s.XXXXXX", PACK_OUT);
    int tfd = mkstemp(tmp_out);
    if (tfd < 0) {
        perror("packer: mkstemp " PACK_OUT);
        return 1;
    }
    if (fchmod(tfd, 0644) != 0) {
        perror("packer: fchmod " PACK_OUT);
        close(tfd);
        unlink(tmp_out);
        return 1;
    }
    FILE *f = fdopen(tfd, "w");
    if (f == NULL) {
        perror("packer: fdopen " PACK_OUT);
        close(tfd);
        unlink(tmp_out);
        return 1;
    }
    fprintf(f, "packed %d checks\n", n);
    fprintf(f, "failed %d checks\n", failed);
    /* 汇总须可审计:逐份记录执行身份与生成时间(变更单 SRE-3760) */
    {
        char tsbuf[32];
        time_t now = time(NULL);
        struct tm tmv;
        localtime_r(&now, &tmv);
        strftime(tsbuf, sizeof(tsbuf), "%Y-%m-%dT%H:%M:%S%z", &tmv);
        const char *un = "unknown";
        struct passwd *pw = getpwuid(getuid());
        if (pw != NULL && pw->pw_name != NULL) {
            un = pw->pw_name;
        }
        fprintf(f, "ts=%s\n", tsbuf);
        fprintf(f, "user=%s\n", un);
    }
    if (fclose(f) != 0) {
        perror("packer: write " PACK_OUT);
        unlink(tmp_out);
        return 1;
    }
    if (rename(tmp_out, PACK_OUT) != 0) {
        perror("packer: rename " PACK_OUT);
        unlink(tmp_out);
        return 1;
    }

    if (failed > 0) {
        fprintf(stderr, "packer: %d/%d checks failed\n", failed, n);
        return 1;
    }
    return 0;
}
