SELECT
  Question_id,
  Question_title,
  Question_body,
  Question_answer_count,
  Question_comment_count,
  Question_created_time,
  Question_favorite_count,
  Question_last_edit_time,
  Question_score_count,
  Question_tags,
  Question_view_count,
  Poster_id,
  Poster_created_time,
  Poster_last_access_time,
  Poster_age,
  Poster_location,
  Poster_reputation_count,
  Poster_view_count,
  Answer_body,
  Answer_comment_count,
  Question_closed_time,
  Answer_last_edit_time,
  Answer_score_count,
  Answerer_id,
  Answerer_created_time,
  Answerer_last_access_time,
  Answerer_age,
  Answerer_location,
  Answerer_reputation_count,
  Answerer_view_count,
FROM (
  SELECT
    owner_user_id,
    id Question_id,
    title Question_title,
    body Question_body,
    accepted_answer_id,
    answer_count Question_answer_count,
    comment_count Question_comment_count,
    creation_date Question_created_time,
    favorite_count Question_favorite_count,
    last_edit_date Question_last_edit_time,
    score Question_score_count,
    tags Question_tags,
    view_count Question_view_count
  FROM
    `bigquery-public-data.stackoverflow.posts_questions`
  WHERE
    REGEXP_CONTAINS(tags, r'azure-machine-learning|clearml|comet-ml|dvc|kedro|mlflow|mlrun|neptune|optuna|python-sacred|sagemaker|vertex-ai|wandb')) Questions
LEFT JOIN (
  SELECT
    id Poster_id,
    creation_date Poster_created_time,
    last_access_date Poster_last_access_time,
    age Poster_age,
    location Poster_location,
    reputation Poster_reputation_count,
    views Poster_view_count
  FROM
    `bigquery-public-data.stackoverflow.users`) Posters
ON
  Posters.Poster_id = Questions.owner_user_id
LEFT JOIN (
  SELECT
    id,
    owner_user_id,
    body Answer_body,
    comment_count Answer_comment_count,
    creation_date Question_closed_time,
    last_edit_date Answer_last_edit_time,
    score Answer_score_count
  FROM
    `bigquery-public-data.stackoverflow.posts_answers`) Answers
ON
  Answers.id = Questions.accepted_answer_id
LEFT JOIN (
  SELECT
    id Answerer_id,
    creation_date Answerer_created_time,
    last_access_date Answerer_last_access_time,
    age Answerer_age,
    location Answerer_location,
    reputation Answerer_reputation_count,
    views Answerer_view_count
  FROM
    `bigquery-public-data.stackoverflow.users`) Answerers
ON
  Answerers.Answerer_id = Answers.owner_user_id;