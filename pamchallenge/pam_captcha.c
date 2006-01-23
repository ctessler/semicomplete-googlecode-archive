#include <sys/types.h>
#include <sys/param.h>
#include <sys/stat.h>

#include <time.h>
#include <sys/uio.h>
#include <fcntl.h>
#include <pwd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>
#include <dirent.h>

#include <security/pam_modules.h>
#include <security/pam_appl.h>

#ifndef PAM_EXTERN
#define PAM_EXTERN
#endif

static char *cows[] = { "head-in", "sodomized", "sheep", "vader", "udder", "mutilated" };
static char *fonts[] = { "standard", "big" };

#define BUFFERSIZE 10240
#define NOLOGINFORYOU "NO SOUP FOR YOU :("
const char alphabet[] = "ABCDEFGHJKMNOPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz123456789$#%@&*+=?";

static void paminfo(pam_handle_t *pamh, char *fmt, ...);
static void pamvprompt(pam_handle_t *pamh, int style, char **resp, char *fmt, va_list ap);

static void figlet(pam_handle_t *pamh, char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);

	char *key;
	FILE *fp = NULL;
	char *buffer, *bp;

	int i;
	char *cow = cows[rand() % (sizeof(cows) / sizeof(*cows))];
	char *font = fonts[rand() % (sizeof(fonts) / sizeof(*fonts))];

	vasprintf(&key, fmt, ap);

	buffer = calloc(BUFFERSIZE, 1);
	srand(time(NULL));

	sprintf(buffer, "/usr/local/bin/figlet -f %s -- '%s' | /usr/local/bin/cowsay -nf %s", font, key, cow);
	fp = popen(buffer, "r");
	i = 0;
	while (!feof(fp)) {
		int bytes;
		bytes = fread(buffer+i, 1, 1024, fp);
		if (bytes > 0)
			i += bytes;

		/* Ooops, our challenge description is too large */
		if (i > BUFFERSIZE)
			return;
	}

	i = 0;
	bp = buffer;
	while (1) {
		char *ptr = strchr(bp, '\n');
		*ptr = '\0';
		//fprintf(stderr, "[%04d / %d] %s\n", (bp - buffer), strlen(bp), bp);
		paminfo(pamh, "%s", bp);
		bp = ptr + 1;
		if (*bp == '\0')
			break;
	}

	free(buffer);
}

static void pamprompt(pam_handle_t *pamh, int style, char **resp, char *fmt, ...) {/*{{{*/
	va_list ap;
	va_start(ap, fmt);
	//fprintf(stderr, "PromptFormat: '%s'\n", fmt);
	pamvprompt(pamh, style, resp, fmt, ap);
	va_end(ap);
}/*}}}*/

static void pamvprompt(pam_handle_t *pamh, int style, char **resp, char *fmt, va_list ap) {/*{{{*/
	struct pam_conv *conv;
	struct pam_message msg, *msgp;
	struct pam_response *pamresp;
	int pam_err;
	char *text = "";

	vasprintf(&text, fmt, ap);

	pam_get_item(pamh, PAM_CONV, (const void **)&conv);
	pam_set_item(pamh, PAM_AUTHTOK, NULL);

	msg.msg_style = style;;
	msg.msg = text;
	msgp = &msg;
	pamresp = NULL;
	pam_err = (*conv->conv)(1, &msgp, &pamresp, conv->appdata_ptr);

	if (pamresp != NULL) {
		if (resp != NULL)
			*resp = pamresp->resp;
		else
			free(pamresp->resp);
		free(pamresp);
	}

	free(text);
}/*}}}*/

static void paminfo(pam_handle_t *pamh, char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	pamvprompt(pamh, PAM_TEXT_INFO, NULL, fmt, ap);
	va_end(ap);
}

static void randomtask(char **task) {
	DIR *dp;
	struct dirent *cur;
	struct dirent *files;
	int pos = 0;
	int len = 20;
	int fd;
	int bytes;

	chdir("/root/dda/");
	dp = opendir(".");
	files = calloc(sizeof(struct dirent), len);

	while ((cur = readdir(dp)) != NULL) {
		if (cur->d_type != DT_REG)
			continue;
		if (cur->d_name[0] == '.')
			continue;
		fprintf(stderr, "File[%d]: %s\n", cur->d_type, cur->d_name);
		files[pos] = *cur;
		pos++;
		if (pos > len) {
			len *= 2;
			files = realloc(files, sizeof(struct dirent) * len);
		}
	}

	pos = rand() % pos;

	//fprintf(stderr, "FILE: %s\n", files[pos].d_name);

	fd = open(files[pos].d_name, O_RDONLY);
	//fprintf(stderr, "Foo: %d\n", fd);
	len = 4096;
	pos = 0;
	*task = calloc(len, 1);

	while ((bytes = read(fd, *task+pos, 1024)) > 0) {
		//fprintf(stderr, "Bytes: %d\n", bytes);
		pos += bytes;
		if (pos >= (len - 1024)) {
			len *= 2;
			*task = realloc(*task, len);
		}

	}
}

/* Dance Dance Authentication {{{ */
static int dda_captcha(pam_handle_t *pamh, int flags, int argc, const char *argv[]) {
	char *resp;
	char *host, *user;
	char key[5];
	char *id;
	char *linkpath;
	char linkdata[1024];
	char *task;
	int i = 0;
	int x;

	pam_get_item(pamh, PAM_RHOST, (const void **)&host);
	pam_get_item(pamh, PAM_USER, (const void **)&user);

	for (i = 0; i < 4; i++)
		key[i] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"[rand() % 36];
	key[4] = 0;

	asprintf(&id, "%s:%s:%s", host, user, key);

	asprintf(&linkpath, "/tmp/%s", id);
	while ((x = symlink(NOLOGINFORYOU, linkpath)) != 0) {
		perror("symlink");
		unlink(linkpath);
	};

	paminfo(pamh, "Welcome to Dance Dance Authentication!!!\n");

	paminfo(pamh, "Dance Dance Authentication requires you to perform a physical task\n"
"to verify that you are a human. Your task is as follows:\n");

	/* read in a list of tasks */
	randomtask(&task);
	paminfo(pamh, task);
	free(task);

	paminfo(pamh, "\nYOUR ID: %s (%s)", key, id);
	pamprompt(pamh, PAM_PROMPT_ECHO_ON, &resp, "Verbally announce your ID when you have completed this task.\n"
"Press enter now and I will permit you to continue once you have completed the task.\n");

	/* loop while task is not completed */
	memset(linkdata, 0, 1024);
	while (linkdata[0] = '\0', readlink(linkpath, linkdata, 1024), !strcmp(linkdata, NOLOGINFORYOU))
		fprintf(stderr, "Waiting...\n"), sleep(1);

	free(id);
	//free(host);
	//free(user);
	free(resp);

	return PAM_SUCCESS;
}/*}}}*/

/* Simple math captcha {{{ */
static int math_captcha(pam_handle_t *pamh, int flags, int argc, const char *argv[]) {
	int x, y, z, answer = 0;
	static char *ops = "+-*";
	char op = ops[rand() % strlen(ops)];
	char *resp = NULL;
	x = rand() % 1000 + 100;
	y = rand() % 1000 + 100;

	paminfo(pamh, "I need some math help.");

	fprintf(stderr, "Math: %d %c %d\n", x, op, y);
	figlet(pamh, "%d %c %d", x, op, y);
	fprintf(stderr, "Figlet done\n");

	pamprompt(pamh, PAM_PROMPT_ECHO_ON, &resp, "Type the solution: ");
	z = atoi(resp);

	switch (op) {
		case '+': answer = x + y; break;
		case '-': answer = x - y; break;
		case '*': answer = x * y; break;
	}

	if (answer != z)
		return PAM_PERM_DENIED;

	return PAM_SUCCESS;
}/*}}}*/

/* String Generation Captcha {{{ */
static int randomstring_captcha(pam_handle_t *pamh, int flags, int argc, const char *argv[]) {
	char key[9];
	char *resp;
	int i = 0;
	int ret = PAM_SUCCESS;

	for (i = 0; i < 8; i++) 
		key[i] = alphabet[rand() % strlen(alphabet)];
	key[8] = 0;

	paminfo(pamh, "Observe the picture below and answer the question listed afterwards:");
	figlet(pamh, key);
	pamprompt(pamh, PAM_PROMPT_ECHO_ON, &resp, "What did the cow say? ");

	if (strcmp(resp, key) != 0)
		ret = (PAM_PERM_DENIED);

	free(resp);
	return ret;
}/*}}}*/

static int (*captchas[])(pam_handle_t *, int, int, const char **) = {
	randomstring_captcha,
	math_captcha,
	dda_captcha
};

PAM_EXTERN int
pam_sm_authenticate(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{
	int r;
	int ret;
	fprintf(stderr, "-\nauthentication started [%d]\n", time(NULL));
	srand(time(NULL));
	r = rand() % (sizeof(captchas) / sizeof(*captchas));
	paminfo(pamh, "[2J[0;0H");
	paminfo(pamh, "If you truely desire access to this host, then you must indulge me in a simple challenge.");
	paminfo(pamh, "-------------------------------------------------------------\n", r);

	ret = captchas[r](pamh, flags, argc, argv);

	if (ret != PAM_SUCCESS) {
		//paminfo(pamh, "Incorrect, perhaps you'll have better luck with another task?");
		sleep(3);
	}
	return ret;
}

PAM_EXTERN int
pam_sm_setcred(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{

	return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_acct_mgmt(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{

    return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_open_session(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{

    return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_close_session(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{

    return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_chauthtok(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{

    return (PAM_SERVICE_ERR);
}

#ifdef PAM_MODULE_ENTRY
PAM_MODULE_ENTRY("pam_captcha");
#endif
