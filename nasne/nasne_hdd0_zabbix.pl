#!/usr/bin/perl

my $curl = 'curl -s "http://192.168.0.104:64210/status/HDDInfoGet?id=0"';

my $cmd;

open(CMD, "$curl |");
$cmd = <CMD>;
#print $cmd;
close(CMD);

if ($cmd =~ /(\"usedVolumeSize\"\: )(\d+)(, \"freeVolumeSize\"\: )(\d+)/){
	#print "used.value $2\n";
	#print "free.value $4\n";
	system("zabbix_sender -z cmn.tmhr.work -s NASUKO -k hdd0_used -o $2");
	system("zabbix_sender -z cmn.tmhr.work -s NASUKO -k hdd0_free -o $4");
}

exit;

