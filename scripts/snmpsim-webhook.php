<?php

$LOCAL_ROOT = "/opt";
$LOCAL_REPO_NAME = "librenms-snmpsim";
$LOCAL_REPO = "{$LOCAL_ROOT}/{$LOCAL_REPO_NAME}";
$REMOTE_REPO = "git@github.com:murrant/librenms-snmpsim.git";
$BRANCH = "master";
$SECRET = "librenms";

if ($_POST['payload'] && $_SERVER['HTTP_X-HUB-SIGNATURE'] === $SECRET) {
    if (is_dir($LOCAL_REPO)) {
        shell_exec("cd {$LOCAL_REPO} && git pull");
    } else {
        shell_exec("cd {$LOCAL_ROOT} && git clone {$REMOTE_REPO}");
    }
    echo("done " . mktime());
} else {
    echo("failed " . mktime());
}
