# Change Control

Changes must remain bounded, preserve fail-closed authority, and update code,
contracts, tests, migrations, and canonical documentation together when those
surfaces are affected. Applied Alembic migrations are immutable; schema changes
receive a new migration.

A pull request records compatibility impact, migration and complete-suite
evidence, health output, documentation assembly and drift evidence, confirmed
mathematical-semantics posture, deferred external operations, and rollback
instructions. Merge and deployment require separate authority.
