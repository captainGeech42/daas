#include <stdio.h>

int get_flag(const char *str) {
	if (str[0] == 'z') {
		puts(str);
		return 0;
	} else {
		puts("no");
		return 1;
	}
}

int main(int argc, char **argv) {
	int ret;

	if (argc != 2) {
		printf("usage: %s <flag>\n", argv[0]);
		return 1;
	}

	ret = get_flag(argv[1]);

	printf("ret value: %d\n", ret);

	return 0;
}
