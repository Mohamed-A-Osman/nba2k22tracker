# Deploying to AWS

The site runs on AWS Lambda behind CloudFront. The stats data lives as Parquet files in S3.
Deploys run from GitHub Actions, so you don't need Docker or SAM installed locally.

Expected cost: about $0/month at friends-level traffic.

## 1. Create the AWS account (one time)

1. Sign up at https://aws.amazon.com and pick the **Free plan**. AWS needs a card to verify
   who you are, but on the Free plan it isn't charged: you spend the sign-up credits, and the
   account pauses when they run out or the plan ends, unless you choose to upgrade.
   Check the current terms on the sign-up page.
2. Turn on MFA for the root user (Account menu -> Security credentials).
3. In IAM, create a user for yourself with the `AdministratorAccess` policy, turn on MFA for it,
   and create an access key for the CLI. Use this user from now on, not root.

## 2. Install the AWS CLI and sign in (one time)

```powershell
winget install Amazon.AWSCLI
aws configure   # paste the access key, region: us-east-1
```

## 3. Let GitHub deploy to your account (one time)

This creates a role that only workflows on this repo's `master` branch can use. No keys are
stored in GitHub.

```powershell
aws cloudformation deploy --template-file deploy/github-oidc.yaml --stack-name nba2k22-github-oidc `
  --capabilities CAPABILITY_NAMED_IAM --parameter-overrides GitHubRepo=Mohamed-A-Osman/nba2k22tracker
aws cloudformation describe-stacks --stack-name nba2k22-github-oidc --query "Stacks[0].Outputs" --output table
```

In GitHub, go to the repo's **Settings -> Secrets and variables -> Actions -> Variables** and add:

| Variable | Value |
|---|---|
| `AWS_DEPLOY_ROLE_ARN` | the `DeployRoleArn` printed above |
| `ALERT_EMAIL` | the email that should get budget alerts |

## 4. Deploy

Go to **Actions -> Deploy to AWS -> Run workflow**. The first run takes about 5-10 minutes,
mostly for CloudFront. The last step prints the site URL.

## 5. Upload the data

Export from your local Postgres, then upload to the data bucket the deploy created:

```powershell
$env:PG_URL = "postgresql://postgres:<password>@localhost/NBA2K22"
python scripts/export_to_parquet.py
# Box-score screenshots: list every folder that holds them; each game keeps one image
python scripts/import_screenshots.py "<screenshot folder>" "<another screenshot folder>"
$bucket = aws cloudformation describe-stacks --stack-name nba2k22tracker `
  --query "Stacks[0].Outputs[?OutputKey=='DataBucketName'].OutputValue" --output text
aws s3 cp data/ "s3://$bucket/data/" --recursive --exclude "screenshots/*"
aws s3 cp data/screenshots/ "s3://$bucket/data/screenshots/" --recursive --content-type image/webp
```

The upload copies the screenshots too (`data/screenshots/`), and CloudFront serves them
straight from S3 at `/screenshots/...`.

Open the site URL. After you upload new data, the site picks it up within about 6 minutes
(1 minute for the app to notice, plus up to 5 minutes of CloudFront caching).

## Keeping costs down

These are already set up by the deploy:

- **Budget alerts** email you when the month's spend passes $1, is forecast to pass $5, or passes $5.
  You can see them under **Billing -> Budgets**.
- **API throttling** limits the site to 5 requests per second (bursts of 10), which caps how much
  anyone can run up the bill.
- **CloudFront caching** means most page views never reach Lambda.

Check **Billing -> Bills** now and then. On the Free plan, **Billing -> Free plan** shows how many
credits are left.

## Deleting everything

```powershell
aws s3 rm "s3://$bucket" --recursive
aws s3api delete-objects --bucket $bucket --delete "$(aws s3api list-object-versions --bucket $bucket --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json)"
aws cloudformation delete-stack --stack-name nba2k22tracker
aws cloudformation delete-stack --stack-name nba2k22-github-oidc
```

The data bucket keeps old versions, so they have to be deleted before the stack can remove it.
The static bucket also needs emptying first (`aws s3 rm s3://<StaticBucketName> --recursive`).
