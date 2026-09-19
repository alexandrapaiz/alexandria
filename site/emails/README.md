# The digest email template

`digest.html` is the newsletter. The reference filler is `docs/design/reviews/2026-09-19/render_sample.py`.

1. Fill by string replacement, no template engine: `{{slot}}` values, plus `<!-- BEGIN:X -->…<!-- END:X -->` regions the filler repeats, fills once, or deletes whole.
2. Issue slots: `{{title}}` (the finding, and the subject line), `{{preheader}}` (one plain sentence for the inbox preview, never the title again), `{{edition}}` ("Daily dispatch · September 19, 2026"), `{{edition_short}}`, `{{opening}}`, `{{close}}`, and the optional `STATS` and `MASTHEAD` regions.
3. Link slots: `{{web_url}}`, `{{archive_url}}`, `{{unsubscribe_url}}` (a `mailto:` is a valid value until a real endpoint exists) and `{{recipient_email}}`.
4. `SECTION` repeats once per H2 and carries `{{section_title}}`: Compounding, New and unproven, Left behind.
5. `ITEM` repeats inside a section; only `{{item_title}}` or `{{item_body}}` is required, and every other region inside it is optional.
6. `ITEM_KIND` is a group label above the item (Contradicted, Replaced) and prints only when it changes, so identical labels never stack.
7. `ITEM_POINT` repeats one procedure line as `{{point_marker}}` plus `{{point}}`; the template owns the bullet, so no list markup is ever passed in.
8. `ITEM_EVIDENCE` carries `{{item_evidence}}`, the in-line grade, read from a line beginning "Evidence:".
9. `ITEM_SOURCE` carries `{{item_source}}` and `{{item_url}}` (the full text, arxiv.org/html when it exists) with `{{item_meta}}` as the visible host and path.
10. Pass values HTML-escaped and typographically normalised (a narrow no-break space becomes a normal one, and none survives before a percent sign), and delete an optional region rather than filling it blank.

No slot narrates the issue's own method, ranking or virtues, by the owner's ruling of 2026-09-19.
