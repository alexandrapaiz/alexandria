### 2026-11-09 - The reading queue's question and read lines are invisible to its own parser, and 888 lines use a separator the parser's docstring does not document (skill seat)

- Trigger: this run appended four lines to `docs/research/reading-queue.md` and
  then checked that the parser reads them, because the charter sends this seat's
  questions to the research seat through that file. `pipeline/reading_queue.py`
  parses 193 rows out of the file and not one of them is a `question` or a
  `read` line. Every such line this seat has ever queued, including the four
  from the v9 revision on the previous pull request, is invisible to it. The
  separator check came out of the same look: the parser's own docstring at line
  39 documents `-- why -- asked by -- date` in ASCII, and the file carries 888
  em dash separators against it, which `tools/ban_list.py` flags one by one.
- What: the parser keys on `arxiv:<id>`, so the queue is two registers sharing
  one file. The half with paper ids is machine-drained by the distill run. The
  half without them, which is every question a seat asks and every non-arXiv
  read, is prose that only a human or an agent reading the whole file will find.
  That is not wrong by itself, and the charter does tell the research seat to
  drain the queue by reading it. What makes it worth filing is that nothing
  distinguishes the two halves to a writer: the format is identical, the
  checkbox is identical, and a seat queueing a question reasonably believes it
  has entered the same pipeline the arXiv lines enter. The separator drift is
  the smaller half of the same shape, a documented format that the file stopped
  following a long time ago with no gate noticing, and this run's four lines use
  the documented ASCII form, which now makes them the only four that do.
- First step: decide which of the two the queue is meant to be, and make the
  file say so. Either teach the parser a second row kind so questions are
  drained by machine, or split the questions into their own section with a
  heading that tells a writer they are read by eye. Either one is an hour. The
  separator is a second hour and is only worth spending if the first answer is
  the parser, because a format nothing reads does not need to be consistent.
- Cost: $0
- Status: proposed
