# Re-archive on consent changes

When a user who has previously had their messages indexed by the wiki bot opts in, replace placeholder links with
the actual text of their messages. 

Possible approaches:

- Bot-side: implement some log of accounts that have been logged and the pages they have been logged to, this would probably
  be a good idea anyway.
- Wiki-side: make a special page that stores that^ information, including links to the initiating messages