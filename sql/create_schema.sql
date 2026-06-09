# Schema Creation in Redshift

CREATE SCHEMA analytics;

# Table Creation

CREATE TABLE analytics.movie_fact (
    movie_id BIGINT,
    title VARCHAR(500),
    release_date DATE,
    popularity FLOAT,
    vote_average FLOAT,
    vote_count BIGINT,
    adult BOOLEAN,
    language VARCHAR(20)
);


# Since the processed data is already in Parquet, we can load directly using COPY command

COPY analytics.movie_fact
FROM 's3://movie-tmdb-data-lake/processed/movies/'
IAM_ROLE 'MY_ROLE_ARN' #Original ARN was replaced during execution
FORMAT AS PARQUET;