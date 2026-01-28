# Snippet Flow

A fast content manager.

----

## How it works:

A task tracker where everything will appear as if it was a scrollable text file. Aim is to make anything quick to insert, edit and find.

In background it will be made of snippets, each one with it's own elements and each will be foldable at the main level. Newer items appear first, below a calendar, search filter and other utilities at the top drawer. Everything is editable in a click, either by clicking directly on the text area or pressing the "edit in full" button at the right tools and data column.

Two columns: The texts column with the foldable icons and titles at the left and, at the right column, are all metadata and toolset for each snippet, like timestamps (last date (and hour if on same day) edited), collaborators and tasks.

When a snippet is showing unfolded, it does not show fully at first, but only some first few lines of body text. How many few is customizable per user. When first clicked, the ellipsed text is then fully shown. The fold icon will revert one step. If a fully shown text is clicked again, then it will be editable in place.

At the tool column some other things that show up are a line of helper buttons ('edit', 'management' etc.), a tasks/phases panel and a grid for linked images. Everything new will always appear first, by creation/insertion date, thought it will also log timestamps for edition per collaborators, with history.

Each snippet is tagged in HTML as an article and separated by horizontal rulers. When a user hovers over a snippet, it's background color change to enhance contrast, if next click triggers editing then mouse icon changes accordingly and the tool set also changes according to current snippet state, like adding a 'save' button where the 'edit' one was, with changed colors in a palette that signals alerts and reversions as friendly as possible.

Each snippet consists of:
  - auto id: createdAt[timestamp];
  - body (and title -- usually as a single markdown text where the first line is always the title, indepently of presence or not of '#' marks);
  - automatically assignments of metadata and tags like currently logged user as current_author (but also re-assignable to any other at full edit/management);
  - data/stats are:
    + list of links and images either at body or at extra links;
    + list of tags + tagged_values to track collaborators and values changing accross time;
      + collaborators and role (coauthor, designer, codesigner, client, reviewer, finisher);
      + communication_channels, (each with an assignable 'finisher' if not the default) which can be picked by users to update as theirs;
    + list of tasks, with some templates and phases wherein some tag should be auto triggered. Ex.: '(pending) text approval', '(pending internal + external) art approval', '(pending) finishing tasks'.
  - all with history of changes, as if each snippet is a single markdown text, with git diffs.

----

_Current DB Schema Quick Overview_:

- (WHERE) class/table += (implicit PK) id + ...
  - Snippet = body + title + timestamp + tasks + tags + FK ( (orig_ & current_) author@role + md_history )
  - Full_Snippet_Vs = md + (optional) diff_sum + FK ( snippet + updated_at + changed_by )
  - User = name + email + pwdhash (+ icon etc)
  - Task = descriptor + is_done + sub_tasks + FK ( at_snippet + has_collaborator@role )
  - Tag = descriptor + (optional) value  # inclusive for timestamps
  - Role = descriptor + FK ( user + snippet || task )
