{
	mexpr=sprintf(".*%s.*",replacekey);
	if (match($0,mexpr)) {
		gsub(replacekey,replacevalue);
		printf("%s\n",$0);
	} else {
		printf("%s\n",$0);
	}
}