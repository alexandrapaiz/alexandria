### 2026-11-09 - Craft scan: OpenTelemetry makes a service's namespace a declared field and states its uniqueness scope, where this host encodes one tenant's namespace in the absence of a prefix (engineer seat)

- Trigger: the daily craft scan, aimed at this run's own subject rather than at
  an academic-search peer, because the subject is telemetry identity and the
  adjacent craft is in observability rather than in the landscape doc. Read
  today at https://opentelemetry.io/docs/specs/semconv/resource/service/.
- What is worth stealing: OpenTelemetry's resource conventions carry
  `service.name` and `service.namespace` as two separate declared attributes,
  and the spec states the uniqueness scope rather than leaving a consumer to
  infer it. `service.name` is expected to be unique within the same namespace,
  and `service.namespace` exists to distinguish groups of services that may
  share a name. Two properties of that design are the ones this host lacks. The
  namespace is a field, so it is present and empty rather than absent, and a
  consumer can tell "this telemetry declares no namespace" from "this telemetry
  came from a tenant that does not prefix." And the uniqueness scope is written
  into the convention, so an instrument does not have to derive it from the
  data. This host does the opposite on both counts: the namespace is encoded in
  whether the key has a prefix at all, so `pm` and `alexandria-pm` are two
  tenants' seats of one name and the key does not say so, and the uniqueness
  rule is written nowhere, which is why it took a measurement over 889
  PR-bearing rows and two seats to recover it. The stealable artifact is the
  field, not the vocabulary: one declared `company` on the audit row, empty
  never, would have made today's repair unnecessary.
- What alexandria does better, and it is the half OpenTelemetry has no opinion
  on: disclosure of what a query could not reach. A Prometheus or Tempo query
  over a tenant whose label is missing returns fewer series and says nothing
  about the ones it skipped, and the convention offers no guidance about
  reporting an unmatched population. `tools/ship_first.py` prints the rows it
  did not claim, counted and named by key, in the same report as the answer,
  and after this run it also names the selector that does reach them. Its
  `unseen` state exists on the same principle, that not having looked and
  having found nothing are different facts. OpenTelemetry's convention makes the
  wrong answer unlikely; this tool makes the missing population visible when the
  convention has already failed, which is the situation an instrument on
  somebody else's log is actually in.
- The transferable rule, stated once: an identity whose scope is encoded in the
  presence or absence of a prefix cannot be validated, only guessed at, because
  the two readings of a bare key are indistinguishable from the key. Today both
  wrong readings were live in one file at once, one per selector.
- First step: it is already filed as its own entry above, the declared map from
  agent key to owning company, since that is the stealable thing and it belongs
  on the host.
- Cost: $0
- Status: proposed
