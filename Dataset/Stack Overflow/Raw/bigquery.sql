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
  Owner_creation_time,
  Owner_last_access_time,
  Owner_location,
  Owner_reputation,
  Owner_up_votes,
  Owner_down_votes,
  Owner_views,
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
    owner_user_id,
    score Question_score,
    tags Question_tags,
    view_count Question_view_count
  FROM
    `bigquery-public-data.stackoverflow.posts_questions`
  WHERE
    REGEXP_CONTAINS(tags, r'azure-machine-learning|clearml|comet-ml|dvc|kedro|mlflow|mlrun|neptune|pachyderm|python-sacred|sagemaker|vertex-ai|wandb')) Questions
JOIN (
  SELECT
    id,
    creation_date Owner_creation_time,
    last_access_date Owner_last_access_time,
    location Owner_location,
    reputation Owner_reputation,
    up_votes Owner_up_votes,
    down_votes Owner_down_votes,
    views Owner_views
  FROM
    `bigquery-public-data.stackoverflow.users`) Owners
ON
  Owners.id = Questions.owner_user_id
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