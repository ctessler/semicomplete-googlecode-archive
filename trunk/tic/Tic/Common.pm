# $Id$
package Tic::Common;

use strict;
use vars ('@ISA', '@EXPORT');
use Exporter;
use Term::ReadKey;
use POSIX qw(strftime);

@ISA = qw(Exporter);
@EXPORT = qw(out real_out error debug query deep_copy prettyprint prettylog
             login set_config get_config expand_aliases);

my $state;

sub set_state { 
	my $self = shift;
	#debug("Setting state for ::Common");
	$state = shift;
}

sub import {
	#debug("Importing from Tic::Common");
	Tic::Common->export_to_level(1,@_);
}

sub out { 
	real_out("\r\e[2K",join("\n",@_) . "\n");
	fix_inputline();
}

sub real_out { print @_; }

sub error {
	print STDERR "\r\e[2K";
	print STDERR "*> " . shift() . "\n"; 
	fix_inputline();
}
sub debug { foreach (@_) { print STDERR "debug> $_\n"; } }

sub fix_inputline {
	# Fix the line
	if (defined($state->{"input_line"})) {
		my $back = (length($state->{"input_line"}) - $state->{"input_position"});
		#real_out($state->{"input_line"});
		real_out(substr($state->{"input_line"},$state->{"leftcol"}, $state->{"termcols"}));
		real_out("\e[" . $back . "D") if ($back > 0);
	}
}

sub prettyprint {
	my ($state, $type, $data) = @_;
	my $output;

	if ($type eq "help") {
		out();
		real_out($data->{"help"} . "\n");
		return;
	}

	if (($state->{"timestamp"}) || (select() ne "main::STDOUT")) {
		my $timestamp;
		if (select() eq 'main::STDOUT') {
			$timestamp = $state->{"config"}->{"timestamp"};
		} else {
			$timestamp = $state->{"config"}->{"logstamp"};
		}

		$output = strftime($timestamp, localtime(time()));
		$output .= " ";
	}

	if (defined(get_config("$type"))) {
		 #$output .= $state->{"config"}->{"$type"};
		 $output .= get_config("$type");

		 # What are the escapes?
		 # %% - literal %
		 # %S - your own screen name
		 # %a - alias name
		 # %c - chatroom related to this message
		 # %e - error message
		 # %g - Group user belongs to
		 # %h - help topic
		 # %i - idle time of user 
		 # %m - Message being sent
		 # %s - Screen name of target (or who is messaging you)
		 # %v - alias value
		 # %w - warning level

		 $data->{"sn"} = getrealsn($state, $data->{"sn"});

		 if (ref($data) eq "HASH") {
		 $output =~ s/%s/$data->{"sn"}/g if (defined($data->{"sn"}));
		 $output =~ s/%m/$data->{"msg"}/g if (defined($data->{"msg"}));
		 $output =~ s/%g/$data->{"group"}/g if (defined($data->{"group"}));
		 $output =~ s/%c/$data->{"chat"}/g if (defined($data->{"chat"}));
		 $output =~ s/%w/$data->{"warn"}/g if (defined($data->{"warn"}));
		 $output =~ s/%i/$data->{"idle"}/g if (defined($data->{"idle"}));
		 $output =~ s/%e/$data->{"error"}/g if (defined($data->{"error"}));
		 $output =~ s/%h/$data->{"subject"}/g if (defined($data->{"subject"}));
		 $output =~ s/%a/$data->{"alias"}/g if (defined($data->{"alias"}));
		 $output =~ s/%v/$data->{"value"}/g if (defined($data->{"value"}));
		 $output =~ s/%S/$state->{"sn"}/g;
		 $output =~ s/%%/%/g;
		 }
	}

	$output =~ s!<(?:(?:(?:html|body|font|b|i|u)(?:\s[^>]+)?)|(?:/(?:html|body|font|b|i|u)))>!!gi;
	$output =~ s!<br>!\n!gi;
	$output =~ s![[:cntrl:]]!!g;

	if ($type =~ m/^error/) {
		error($output);
	} else {
		#out("< $type > $output");
		out($output);
	}
}

sub prettylog {
	my ($state, $type, $data) = @_;
	if (defined($data)) {
		if (defined($data->{"sn"})) {
			my $sn = getrealsn($state,$data->{"sn"});
			open(IMLOG, ">> ".$ENV{HOME}."/.tic/" . $sn . ".log") or 
				die("Failed trying to open ~/.tic/".$sn.".log - $!\nEvent: $type\n");
			select IMLOG;
			prettyprint(@_);
			select STDOUT;
			close(IMLOG);
		}
	}
}

sub query {
	my ($q, $hide) = @_;
	real_out("$q");
	ReadMode(0) unless ($hide);
	chomp($q = <STDIN>);
	ReadMode(3);
	real_out("\n") if ($hide);
	return $q;
}

sub deep_copy {
	my ($data) = shift;
	my $foo;

	if (ref($data) eq "HASH") {
		map { $foo->{$_} = $data->{$_} } keys(%{$data});
	}
	return $foo;
}

sub getrealsn {
	my ($state,$sn) = @_;
	my $foo = $state->{"aim"}->buddy($sn);
	return $foo->{"screenname"} if (defined($foo->{"screenname"}));
	return $sn;
}

sub login {
	my ($user,$pass) = @_;
	my ($fail) = 0;

	do {
		$user = $pass = undef if ($fail > 0);
		while (length($user) == 0) {
			$user = query("login: ");
		}
		$pass = query("password: ", 1) if (length($pass) == 0);
		$fail++;
	} while (length($pass) == 0);

	$state->{"signon"} = 1;
	$state->{"aimok"} = 1;
	out("Logging in to AIM, please wait :)");
	my %hash = ( screenname => $user, 
					 password => $pass );
	$hash{"port"} = $state->{"settings"}->{"port"} || "5190";
	$hash{"host"} = $state->{"settings"}->{"host"} || "login.oscar.aol.com";

	out("Connecting to " . $hash{"host"} . ":" . $hash{"port"} . " as " . $hash{"screenname"});
	$state->{"aim"}->signon(%hash);
}

sub get_config {
	my ($a) = @_;
	#out("$state | get_config($a) = " . $state->{"config"}->{$a});
	return $state->{"config"}->{$a};
}

sub set_config {
	my ($a,$b) = @_;
	#out("$state | set_config($a,$b)");
	$state->{"config"}->{$a} = $b;
}

sub expand_aliases {
	my ($string) = shift;
	my ($cmd,$args) = split(/\s+/, $string, 2);
	my ($commands, $aliases) = ($state->{"commands"}, $state->{"aliases"});

	if ($cmd =~ s!^/!!) {
		if (defined($commands->{$cmd})) {
			return "/$cmd $args";
			#&{$commands->{$cmd}}($state, $args);
		} elsif (defined($aliases->{$cmd})) {
			$state->{"recursion_check"}++;
			if ($state->{"recursion_check"} > 10) {
				out("Too much recursion in this alias. Aborting execution");
				return;
			}  
			($cmd, $args) = $aliases->{$cmd} . " " . $args;
			return expand_aliases($cmd,$args);
			$state->{"recursion_check"}--;
		}
	} 
}

1;

