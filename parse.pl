#!/usr/bin/env perl
use strict;
use warnings;
use autodie;
use feature qw(say);
use utf8;
binmode STDOUT, ':encoding(UTF-8)';
use JSON::DWIW;
use Term::ANSIColor;
use Term::ReadLine;
## cpan JSON::DWIW Term::ANSIColor Term::ReadLine

my $show_allowed_answer = 1;
my $show_importance = 1;
my $file = '../data/questions.json';
$file = shift if @ARGV;
unless (-r $file) {
    say "File $file is not readable: $!";
    say 'Please give me a JSON file as parameter …';
    exit 1;
}

my $cli = Term::ReadLine->new;

# if ($^O eq "MSWin32" || $^O eq "dos")
# {
#     open(my $INPUT, "<con") and $cli->newTTY($INPUT, $cli->OUT);
# }

sub int_h { say "\nExiting. Have a nice day …"; exit 0 }
local $SIG{'INT'} = 'int_h';

#<<<
my @importance = (
    'Irrelevant',
    colored('A little important', 'green'),
    colored('Somewhat important', 'underline green'),
    colored('Very important', 'red on_bright_yellow'),
    colored('Mandatory', 'bright_red on_black'),
);
#>>>

my $json_parser = JSON::DWIW->new;
my $que         = $json_parser->from_json_file($file);
my $date        = $que->{date};
print "The data is from $date\n\n";

sub printIt {
    my $que_id  = shift;
    my $pattern = shift;

    chomp( my $text = $que->{data}->{$que_id}->{text} );
    ## There are sometimes newlines at the end …

    if ( defined $pattern ) {
        $text =~ /$pattern/ms; ## no critic (RegularExpressions::RequireExtendedFormatting)
        $text = ${^PREMATCH} . colored( ${^MATCH}, 'blue' ) . ${^POSTMATCH};
    }

    if ( $que->{data}->{$que_id}->{isSkipped} ) { ## The question is skipped
        say "$que_id was skipped: $text";
    }
    else {
        my $imp = $que->{data}->{$que_id}->{importance};
        my $exp = $que->{data}->{$que_id}->{explanation};
        my $pub = $que->{data}->{$que_id}->{isPublic};
        my $visability = $pub ? 'publicly' : 'privately';
        my $imp_text = $show_importance ? "$imp: $importance[$imp], " : '';
        say "$text ($imp_text$visability answered):";
        for my $ans_id ( sort { $a <=> $b } keys $que->{data}->{$que_id}->{answers} ) {
            my $ans_text  = $que->{data}->{$que_id}->{answers}->{$ans_id}->{text};
            my $my_ans    = $que->{data}->{$que_id}->{answers}->{$ans_id}->{isMine};
            my $match_ans = $que->{data}->{$que_id}->{answers}->{$ans_id}->{isMatch};
            print color 'underline' if $my_ans;
            if ($match_ans and $show_allowed_answer) {
                print color 'green';
            }
            print "\t$ans_text" . color 'reset';
            print " ($exp)" if ( $my_ans and $exp );
            print "\n";
        }
    } ## end else [ if ( $que->{data}->{$que_id...})]
    print "\n";
} ## end sub printIt

## Building a query hash
my %qQue;
for my $que_id ( keys $que->{data} ) {
    chomp( my $text = $que->{data}->{$que_id}->{text} );
    ## There are sometimes newlines at the end …
    $qQue{$text} = $que_id;
}

say 'You can use a perl regular expression to match against the questions.';
say 'The regular expression is case insensitive.';
say 'If you are done you can enter a empty pattern to exit the program.';
while (1) {
    my $pattern = $cli->readline('Please enter a pattern: ');
    if ("$pattern" =~ /\A\s*\Z/xms) {
        say 'Have fun';
        last;
    }

    my @matches = eval {
        grep { /$pattern/msi } keys %qQue ## no critic (RegularExpressions::RequireExtendedFormatting)
    };
    if ($@) {
        say 'Your regular expresion failed';
        print "Error: $@";
        next;
    }

    my @que_id = map { $qQue{$_} } @matches;
    my $word_times = 'time';
    my $match_count = @matches;
    $word_times .= "s" unless $match_count == 1;
    say 'Matched ' . $match_count . " $word_times:";
    if ( $match_count > 20 ) {
        print 'Do you really want to print all questions? ';
        my $user_answer = <>;
        next unless ( $user_answer =~ /\A(?:y|j)/xmsi );
    }
    for my $que_id ( sort { $a <=> $b } @que_id ) {
        printIt $que_id, $pattern;
    }
} ## end while (1)
