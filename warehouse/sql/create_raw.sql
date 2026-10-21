-- Raw layer: an exact copy of the CSV files, one table per source.
-- Every column is text on purpose: raw data is loaded as it is, so a bad
-- value can never make the load fail. Types are applied later in dbt staging.
-- Two technical columns are added to every table:
--   _source_file  which CSV file the row came from (path inside the repository)
--   _loaded_at    when the loader inserted the row

create schema if not exists raw;

create table if not exists raw.players (
    collected_at_utc text,
    appid            text,
    game             text,
    role             text,
    player_count     text,
    status           text,
    _source_file     text not null,
    _loaded_at       timestamptz not null default now()
);

create table if not exists raw.reviews (
    recommendation_id           text,
    appid                       text,
    language                    text,
    created_utc                 text,
    updated_utc                 text,
    voted_up                    text,
    votes_up                    text,
    votes_funny                 text,
    weighted_vote_score         text,
    comment_count               text,
    steam_purchase              text,
    received_for_free           text,
    written_during_early_access text,
    refunded                    text,
    primarily_steam_deck        text,
    playtime_at_review_min      text,
    playtime_forever_min        text,
    author_num_reviews          text,
    has_developer_response      text,
    review_length               text,
    fetched_at_utc              text,
    _source_file                text not null,
    _loaded_at                  timestamptz not null default now()
);

create table if not exists raw.games (
    appid        text,
    game         text,
    role         text,
    reviews      text,
    _source_file text not null,
    _loaded_at   timestamptz not null default now()
);

create table if not exists raw.events (
    event_id     text,
    event_date   text,
    end_date     text,
    appid        text,
    game         text,
    event_type   text,
    event_name   text,
    magnitude    text,
    source_url   text,
    notes        text,
    _source_file text not null,
    _loaded_at   timestamptz not null default now()
);

-- Which files were loaded, with a fingerprint (SHA-256) of their content.
-- If a file has not changed since the last load, the loader skips it.
create table if not exists raw.load_log (
    source_file  text primary key,
    target_table text not null,
    sha256       text not null,
    row_count    integer not null,
    loaded_at    timestamptz not null default now()
);

-- Speeds up "delete the old rows of this file" when a file is reloaded.
create index if not exists ix_players_source on raw.players (_source_file);
create index if not exists ix_reviews_source on raw.reviews (_source_file);
