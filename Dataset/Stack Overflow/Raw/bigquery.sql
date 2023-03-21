SELECT
  Question_id,
  Question_title,
  Question_body,
  Question_answer_count,
  Question_comment_count,
  Question_creation_time,
  Question_favorite_count,
  Question_last_edit_time,
  Question_score,
  Question_tags,
  Question_view_count,
  Answer_body,
  Answer_comment_count,
  Answer_creation_time,
  Answer_last_edit_time,
  Answer_score
FROM (
  SELECT
    id Question_id,
    title Question_title,
    body Question_body,
    accepted_answer_id,
    answer_count Question_answer_count,
    comment_count Question_comment_count,
    creation_date Question_creation_time,
    favorite_count Question_favorite_count,
    last_edit_date Question_last_edit_time,
    score Question_score,
    tags Question_tags,
    view_count Question_view_count
  FROM
    `bigquery-public-data.stackoverflow.posts_questions`
  WHERE
    REGEXP_CONTAINS(tags, r'azure-machine-learning|clearml|comet-ml|dvc|kedro|mlflow|mlrun|neptune|optuna|python-sacred|sagemaker|vertex-ai|wandb')) Questions
LEFT JOIN (
  SELECT
    id,
    body Answer_body,
    comment_count Answer_comment_count,
    creation_date Answer_creation_time,
    last_edit_date Answer_last_edit_time,
    score Answer_score
  FROM
    `bigquery-public-data.stackoverflow.posts_answers`) Answers
ON
  Answers.id = Questions.accepted_answer_id;