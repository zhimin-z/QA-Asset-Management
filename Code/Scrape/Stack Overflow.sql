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
  Question_comment_body,
  Question_comment_score,
  Poster_id,
  Poster_reputation_count,
  Poster_view_count,
  Poster_upvotes,
  Poster_downvotes,
  Answer_body,
  Answer_comment_count,
  Question_closed_time,
  Answer_last_edit_time,
  Answer_score_count,
  Answerer_id,
  Answerer_reputation_count,
  Answerer_view_count,
  Answerer_upvotes,
  Answerer_downvotes,
  Answer_comment_body,
  Answer_comment_score
FROM (
  SELECT
    OwnerUserId,
    Id Question_id,
    Title Question_title,
    Body Question_body,
    AcceptedAnswerId accepted_answer_id,
    AnswerCount Question_answer_count,
    CommentCount Question_comment_count,
    CreationDate Question_created_time,
    FavoriteCount Question_favorite_count,
    LastEditDate Question_last_edit_time,
    Score Question_score_count,
    Tags Question_tags,
    ViewCount Question_view_count
  FROM
    Posts) Questions
LEFT JOIN (
  SELECT
    Id Poster_id,
    Reputation Poster_reputation_count,
    Views Poster_view_count,
    UpVotes Poster_upvotes,
    DownVotes Poster_downvotes
  FROM
    Users) Posters
ON
  Posters.Poster_id = Questions.OwnerUserId
LEFT JOIN (
  SELECT
    id Answer_id,
    OwnerUserId,
    Body Answer_body,
    CommentCount Answer_comment_count,
    CreationDate Question_closed_time,
    LastEditDate Answer_last_edit_time,
    Score Answer_score_count
  FROM
    Posts) Answers
ON
  Answers.Answer_id = Questions.accepted_answer_id
LEFT JOIN (
  SELECT
    AccountId Answerer_id,
    Reputation Answerer_reputation_count,
    Views Answerer_view_count,
    UpVotes Answerer_upvotes,
    DownVotes Answerer_downvotes
  FROM
    Users) Answerers
ON
  Answerers.Answerer_id = Answers.OwnerUserId
LEFT JOIN (
    SELECT
        PostId,
        STRING_AGG(CAST(Text AS NVARCHAR(MAX)),' ') Question_comment_body,
        SUM(Score) AS Question_comment_score
    FROM Comments QC
    GROUP BY PostId
) Question_comments 
ON
  Question_comments.PostId = Questions.Question_id
LEFT JOIN (
    SELECT
        PostId,
        STRING_AGG(CAST(Text AS NVARCHAR(MAX)),' ') Answer_comment_body,
        SUM(Score) AS Answer_comment_score
    FROM Comments AC
    GROUP BY PostId
) Answer_comments 
ON
  Answer_comments.PostId = Answers.Answer_id
WHERE
  Question_tags LIKE '%azure-machine-learning%'OR 
  Question_tags LIKE '%clearml%' OR 
  Question_tags LIKE '%comet-ml%' OR
  Question_tags LIKE '%dvc%' OR
  Question_tags LIKE '%h2o.ai%' OR
  Question_tags LIKE '%kedro%' OR
  Question_tags LIKE '%mlflow%' OR
  Question_tags LIKE '%mlrun%' OR
  Question_tags LIKE '%neptune%' OR
  Question_tags LIKE '%optuna%' OR
  Question_tags LIKE '%python-sacred%' OR
  Question_tags LIKE '%sagemaker%' OR
  Question_tags LIKE '%vertex-ai%' OR
  Question_tags LIKE '%wandb%'