resource "aws_lambda_function" "query" {
  function_name = "${var.project}-query"
  role          = aws_iam_role.lambda.arn
  handler       = "app.handlers.query.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 512
  filename      = "../lambda.zip"
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.chunks.name
      S3_BUCKET      = aws_s3_bucket.main.id
    }
  }
}
resource "aws_cloudwatch_log_group" "query" {
  name              = "/aws/lambda/${aws_lambda_function.query.function_name}"
  retention_in_days = 7
}
