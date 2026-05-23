# 每周 GitHub 热门项目邮件

这个自动化每周一北京时间 09:00 运行，抓取上周 GitHub 热门项目 Top 10，并发送到 `xinhongyuan2023@gmail.com`。

## 必需 Secret

在仓库页面进入 `Settings` -> `Secrets and variables` -> `Actions`，新增：

- `GMAIL_APP_PASSWORD`：Gmail 应用专用密码

Gmail 应用专用密码不是 Gmail 登录密码。需要先在 Google 账号里开启两步验证，再创建 App Password。

## 手动运行

进入 GitHub 仓库的 `Actions` 页面，选择 `Weekly GitHub Trending Email`，点击 `Run workflow` 即可手动发送一次。

## 统计口径

脚本查询上一周新建的公开 GitHub 仓库，按当前 star 数降序取前 10。GitHub 没有官方 Trending API，这里使用 GitHub Search API 作为稳定替代。
