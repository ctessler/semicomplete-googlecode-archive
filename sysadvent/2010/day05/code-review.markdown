# Hey Sysadmins, Why Aren't You Doing code review Already?

_This article was written by [Phil Hollenback](http://www.hollenback.net) and is [@philiph](http://twitter.com/philiph) on Twitter._

I have to admit: I'm on the fence about the devops movement.  However, I do
think there are a lot of good ideas to be found in the 'devops culture'. One
idea I particularly like is that sysadmins should think more like developers.
I might be partly attracted to that philosophy because I have a CS degree.
However, I also think it's logical because developers have spent a lot of time
figuring out development workflows (duh).  With the increasing automation in
system administration, it's natural that we as sysadmins should follow the same
process.  Whether we like it or not, we will all be writing more code in the
years to come as we increase our use of automation.

I hear that developers are all het up about Agile programming these days.  I
don't know a lot about that whole methodology either, but I have found some
good ideas from skimming the literature.  One idea that really excites me as a
sysadmin is the notion of code review. Someone once said something like, "with
enough eyes, all bugs are shallow" and that is exactly what code review
accomplishes.  My group has embraced code review as an operational concept and
it has greatly increased the quality of our work.  Thus, I'm here to spread the
word: everyone should be doing code review on any scripts, programs, or text
config files destined for production.

## THE TOOLS

In my workplace our code review tools are Bugzilla, Subversion, and Review
Board.  There are other code review products out there but we already had Review
Board (http://www.reviewboard.org) set up so it was an obvious choice.  This
process is tool-agnostic: you could use any combination of version control, bug
tracker, and code review if you wanted.

The first step in the process is to create a tracking bug.  In my organization
we say "if there isn't a bugzilla, it doesn't exist".  Don't waste my time with
an email thread.  The bug will be used for all subversion commit messages and
will be referenced in the review board posting.  We use a subversion post-hook
that requires all log messages to include a bugzilla reference to help enforce
this.

Once you have the bug/ticket/issue, you check the existing files out of subversion and
make your changes.  Note that we have a lot of YAML-formatted text config files
that we keep in subversion as well, so we use code review for changes to those
as well.

Now you have a subversion diff you can submit to Review Board.  You might want
to run 'svn diff' to sanity check your diff before submitting.  If you like
what you see, submit your code review like this (from your subversion working
directory):

    $ post-review -p --bugs-closed 12345 --description "fix fencepost error" \
      --summary "system healthcheck scripts" --target-group sysadmins

The above will create your code review, publish it, and reference the bugzilla
from the first step.  It will also send an email out to the 'sysadmins' group
which you've already configured in Review Board.  That email contains a link to
the review in Review Board.  Here's what the main screen for a pending
code review request looks like:

![review main screen](http://lh6.ggpht.com/_u-5lMShiO40/TPtZVsjU5oI/AAAAAAAAAFg/J7QdSyht4Jw/review%20main%20screen.jpg)

The next step is up to the reviewers.  Typically you will send a code review to
a group of reviewers, and wait for any one of them to sign off on your review.
Review Board allows reviewers to make general comments about all the diffs in a
review, and/or comments on specific line numbers.

Viewing the diff for a change:

![view the diff](http://lh3.ggpht.com/_u-5lMShiO40/TPtZVT0a4LI/AAAAAAAAAFw/9m0l4jzitYI/view%20diff.jpg)

Adding a comment to a specific line number:

![adding a comment](http://lh4.ggpht.com/_u-5lMShiO40/TPtZVnCaXQI/AAAAAAAAAFo/BwWVKHwPIF0/adding%20a%20comment.jpg)

Once a reviewer is satisfied with all their comments, they publish their review
so you can see it.  They can either select the 'ship it!' button or leave it
unchecked, depending on whether or not they feel your changes are acceptable.
If the reviewer doesn't check 'ship it!', the expectation is that you will fix
the problems and submit another review request.  Review Board supports review
revisions via using the '-r' option to post-review, so you don't need to create
multiple review requests.

![ship it](http://lh5.ggpht.com/_u-5lMShiO40/TPtZVXzUlWI/AAAAAAAAAF4/0A19I7OKC9Q/ship%20it.jpg)

Continue this iterative process for adjusting your code until your reviewer
signs off by checking the 'ship it!' button on their review.  Congratulations,
you now have a code review change!  Go check it in to subversion and prepare
for deployment.

WHY DO ALL THIS WORK?

While the effort to generate code review is not terribly substantial, it does
complicate your workflow.  Why do this at all?  One simple reason: it makes
your code or config files better!  This is due to several reasons:

1. If you work in an environment where code review is the norm, you
   unconsciously write better code because you know someone is going to look at
   it.  Maybe it doesn't always work out that way, but I know I stop myself
   form doing sloppy things if I know someone is going to critique my work.
2. Code review serves as a final check to catch stupid mistakes.  You are blind
   to dumb typos in your own code.  Other reviewers tend to find them with much
   more regularity.  This is largely because they don't know the flow of your
   code so they have to look through it all carefully.
3. Code review serves as a barrier for, lets say, "less experienced" peers.  You
   all know what I'm saying here.  Often people are afraid to admin they don't
   know how to fix some problem assigned to them. Solution? Take a best guess
   shot in the dark and pray it works.  My classic example: I asked a sysadmin
   once to randomize his cronjob running on many servers as to not overload a
   particular service.  He did the work and we put the new script into
   production on several thousand machines.  Then we started seeing regular
   overloads on the service in question at the same time every hour.  When we
   inspected the randomized code, we found the sysadmin had picked a random
   time delay value and then used THE SAME VALUE on every host.  If you don't
   do code review you don't find problems like this.
4. A real benefit that should not be overlooked is that code review can be an
   incredible learning tool for both junior and senior sysadmins.  Junior
   sysadmins need to learn about everything so your feedback helps them
   immediately.  The effect with senior sysadmins is more subtle.  We are
   creatures of habit and develop our coding techniques early in our career.
   Tools evolve and we often don't bother to follow up on advancements.  If
   someone else reviews your code, that gives them an opportunity to suggest
   better approaches to problems.  This can be a real eye-opener if you haven't
   read the manuals in a while.
5. Code and configuration style and quality can be enforced. If you have a
   style guide (you should!), you can use code review to both enforce style and
   educate about style. You can enforce code-style spacing, usage, etc, and also
   enforce larger concepts like requiring tests for each change, etc.

One thing to keep in mind is that code review is actually easier and less
time-consuming for sysadmins than for developers.  Developers write code all
the time, and they write a lot of code.  Sysadmins typically perform many
duties besides writing scripts, and thus the amount of review work is
correspondingly reduced.  In our experience in a group of 6 people, code review
create a minimal amount of overhead.

## CONCLUSION

I'm here to tell you that code review works, and it works particularly well for
system administrators.  Formalized code review is a rising tide that lifts all
boats - we all write better code and configurations when others look at it.
Review Board in particular provides a fairly simple and lightweight way to
implement code review. Code review is your first line of defense in many ways.
When a script breaks in production, the first thing I say is, "was it code
reviewed"?

Everyone knows that question is going to be asked so we plan accordingly and
write better code.  I'm not talking about large coding projects here either -
even the simplest of scripts should be code reviewed.  In fact, small scripts
can benefit the most because those are the ones you are most likely to write
quickly and carelessly. So please take my recommendations to heart - implement
a code review culture for system administration.  It will have a measurable
effect on your team's performance and will definitely reduce production
outages.

Further reading:

* [The Review Board](http://www.reviewboard.org)
* [Four Ways to a Practical Code Review](http://www.methodsandtools.com/archive/archive.php?id=66)
