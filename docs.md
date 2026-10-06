# 数据

本文档逐个说明 `data/` 下各 CSV 的**原始字段及其含义**。

- 字段含义优先采用官方说明 `VariableDefinitions.csv`。官方没有说明的字段，只按字段名的字面意思解释，并标注"官方未定义"。
- 取值统计基于全部原始数据，未做任何过滤或加工。

## 0. 总览

| 文件 | 行数 | 列数 | 一行代表 |
|---|---|---|---|
| Users.csv | 12,413 | 8 | 一个用户 |
| UserActivity.csv | 317,292 | 6 | 用户的一条站内活动记录 |
| CompetitionPartipation.csv | 8,385 | 8 | 用户报名一个比赛 |
| Discussion.csv | 1,439 | 9 | 用户发起的一个讨论帖 |
| Comments.csv | 467 | 6 | 用户在讨论帖下的一条评论 |
| Competition.csv | 247 | 20 | 一个比赛 / 黑客松 |
| Blogs.csv | 117 | 6 | 一篇博客 |
| Jobs.csv | 34 | 7 | 一个职位 |
| SampleSubmission.csv | 1,340 | 2 | 一个需要提交预测的用户 |
| VariableDefinitions.csv | 62 | 2 | 一个字段的官方说明 |

### 表之间的关联字段

| 从 | 字段 | 到 |
|---|---|---|
| UserActivity / CompetitionPartipation / Discussion / Comments | `User_ID` | Users |
| CompetitionPartipation / Discussion | `Competition ID` | Competition（`Comp_ID`） |
| Comments | `Disc_ID` | Discussion |
| UserActivity | `Title` 形如 `comp_ID_xxx` / `blog_ID_xxx` / `job_ID_xxx` | Competition / Blogs / Jobs |

以上关联已核对过，所有 ID 都能在目标表中找到对应记录。

### 时间字段（所有表通用）

时间被拆成四列：`... time`（时分秒）、`... Year`、`... Month`、`... Day_of_month`。

官方说明如下：

> Years are in chronological order. Months are in chronological order but January is not necessarily month 1.
> The variables have been masked consistently across all tables.

即年份和月份都经过脱敏，编码保持了先后顺序，但月份编码 1 不一定是一月。各表的脱敏方式一致。

---

## 1. Users.csv：用户

| 列 | 官方含义 | 取值 |
|---|---|---|
| `User_ID` | 用户唯一 ID，可用于关联讨论、评论、提交等表 | 12,413 个，无重复 |
| `FeatureX` | 用户所属的某个类别（已脱敏） | 0：11,354；1：1,059 |
| `FeatureY` | 用户所属的某个类别（已脱敏） | 0：8,114；1：3,170；3：1,129 |
| `Countries_ID` | 用户所在国家（已脱敏，与 Competition 表的国家编码方式相同） | 146 个国家，缺失 47.4% |
| `Created At time` | 注册时刻 | 精确到微秒 |
| `Created At Year` | 注册年份 | 只有 1 |
| `Created At Month` | 注册月份 | 7 个编码：11（1,262）、12（1,982）、1（1,504）、2（2,278）、3（2,000）、4（1,382）、5（2,005） |
| `Created At Day_of_month` | 注册日 | 1–31 |

---

## 2. UserActivity.csv：用户站内活动

| 列 | 含义 | 取值 |
|---|---|---|
| `User_ID` | 用户 | 10,400 个用户 |
| `Title` | 活动名称（官方未定义） | 397 种 |
| `datetime time` | 发生时刻 | 精确到秒 |
| `datetime Year` | 年份 | 只有 1 |
| `datetime Month` | 月份 | 7 个编码，与 Users 相同 |
| `datetime Day_of_month` | 日 | 1–31 |

`Title` 的取值分为两种形式。

### 2.1 文字形式的活动名称（34 种）

按记录数从高到低排列。中文是字面翻译。

| Title | 字面含义 | 记录数 | 用户数 |
|---|---|---|---|
| Viewed All Competitions | 查看比赛列表 | 58,176 | 9,734 |
| Viewed All Discussions | 查看讨论列表 | 47,172 | 10,282 |
| Viewed All Learning Pages | 查看学习页面列表 | 22,930 | 9,263 |
| Downloaded Competition Datafile | 下载比赛数据文件 | 19,578 | 3,255 |
| Updated Profile | 更新个人资料 | 14,748 | 3,378 |
| Created Submission | 创建提交 | 13,649 | 1,047 |
| $identify | （以 `$` 开头，无字面含义） | 12,339 | 8,864 |
| Signed Up | 注册 | 10,862 | 10,336 |
| $create_alias | （以 `$` 开头，无字面含义） | 9,346 | 8,756 |
| Confirmed Email | 确认邮箱 | 8,818 | 8,441 |
| Updated Discussion | 更新讨论 | 6,498 | 706 |
| Joined Competition | 加入比赛 | 6,086 | 4,393 |
| Viewed All Jobs | 查看职位列表 | 4,139 | 1,484 |
| Signed In | 登录 | 4,100 | 2,366 |
| Updated Submission | 更新提交 | 2,929 | 479 |
| Signed Out | 登出 | 1,660 | 833 |
| Viewed Discussion | 查看讨论 | 1,207 | 430 |
| Updated Comment | 更新评论 | 656 | 234 |
| Joined Team | 加入队伍 | 384 | 376 |
| Invited Member To Team | 邀请成员加入队伍 | 344 | 299 |
| Created Team | 创建队伍 | 310 | 288 |
| Votes (Up/Down) | 投票（赞 / 踩） | 149 | 68 |
| Applied To Job | 申请职位 | 126 | 56 |
| Viewed FAQ | 查看常见问题 | 104 | 68 |
| Updated Team | 更新队伍 | 42 | 31 |
| Deleted Team | 删除队伍 | 28 | 27 |
| Transferred Team Leadership | 转让队长 | 14 | 14 |
| Updated Discussion Team Participants | 更新讨论的队伍成员 | 10 | 8 |
| Accepted Team Leadership Transfer | 接受队长转让 | 9 | 9 |
| Changed Password | 修改密码 | 5 | 5 |
| Left Team | 离开队伍 | 4 | 4 |
| Kicked Member From Team | 将成员移出队伍 | 3 | 3 |
| Revoked Team Leadership Transfer | 撤销队长转让 | 1 | 1 |
| Report Something | 举报 | 1 | 1 |

### 2.2 "前缀_ID"形式（363 种）

| 形式 | 字面含义 | 不同取值 | 记录数 | 用户数 | 对应表 |
|---|---|---|---|---|---|
| `comp_ID_xxx` | 某个比赛 | 229 | 55,540 | 5,451 | Competition.csv |
| `blog_ID_xxx` | 某篇博客 | 100 | 2,712 | 1,041 | Blogs.csv |
| `job_ID_xxx` | 某个职位 | 30 | 1,492 | 626 | Jobs.csv |
| `badge_xxx` | 某个徽章 | 4 | 11,121 | 8,489 | 无对应表 |

`badge_xxx` 的 4 个取值：`badge_OCZE`（8,864）、`badge_HYIO`（1,760）、`badge_MLPD`（457）、`badge_PLDS`（40）。

---

## 3. CompetitionPartipation.csv：比赛报名

| 列 | 官方含义 | 取值 |
|---|---|---|
| `User_ID` | 报名比赛的用户 | 5,245 个用户 |
| `Competition ID` | 所报名的比赛 | 131 个 |
| `Participant Type` | 参赛者类型（官方未定义） | 只有 1 |
| `Successful Submission Count` | 成功提交次数，按每 10 次分组，分组编号已脱敏（count 3 不一定表示 30–40 次） | `count 10`：1,044；`count 6`：169；`count 8`：95；`count 9`：49；`count 3`：41；`count 7`：29；`count 5`：15；`count 4`：7；缺失 82.7% |
| `Created At time / Year / Month / Day_of_month` | 报名时间 | Year 只有 1 |

---

## 4. Discussion.csv：讨论帖

| 列 | 官方含义 | 取值 |
|---|---|---|
| `Disc_ID` | 讨论帖唯一 ID，可与 Comments 表关联 | 1,439 个，无重复 |
| `User_ID` | 发帖用户，可与 Users 表关联 | 1,017 个用户 |
| `Competition ID` | 帖子所属的比赛（官方未定义） | `GeneralDiscussion`：986 条（68.5%），其余分属 48 个比赛 |
| `Personal` | 字面含义为"个人的"（官方未定义） | 1：1,159；0：280 |
| `Theme` | 主题（官方未定义；官方说明中对应的字段可能是 FeatureF："讨论帖所属类别，已脱敏"） | 1：71；5：34；3：30；4：14；2：10；缺失 89.0% |
| `Created At time / Year / Month / Day_of_month` | 发帖时间 | Year 只有 1 |

---

## 5. Comments.csv：评论

| 列 | 官方含义 | 取值 |
|---|---|---|
| `Disc_ID` | 评论所在的讨论帖 | 90 个讨论帖 |
| `User_ID` | 发表评论的用户 | 192 个用户 |
| `Created At time / Year / Month / Day_of_month` | 评论时间 | Year 只有 1；Month 只出现 4 个编码：1（404）、12（34）、2（16）、5（13） |

---

## 6. Competition.csv：比赛

| 列 | 官方含义 | 取值 |
|---|---|---|
| `Comp_ID` | 比赛或黑客松的 ID | 247 个，无重复 |
| `FeatureA` | 比赛所属类别（已脱敏） | 列表形式，如 `[2, 4]`、`[]`；28 种 |
| `FeatureB` | 比赛所属类别（已脱敏） | 列表形式；20 种 |
| `FeatureC` | 比赛所属类别（已脱敏） | 1–37；缺失 20.6% |
| `FeatureD` | 比赛所属类别（已脱敏） | 0：133；1：114 |
| `FeatureE` | 比赛所属类别（已脱敏） | 1：19；2：167；3：61 |
| `FeatureF` | 官方未定义（官方说明中的 FeatureF 属于讨论表） | 列表形式；23 种 |
| `FeatureG` | 官方未定义（官方说明中的 FeatureG 属于提交表） | `[]`：132；`[5]`：60；`[3]`：38；`[4]`：16；`[5, 3, 4]`：1 |
| `FeatureH` | 官方未定义 | 列表形式；18 种 |
| `FeatureI` | 官方未定义 | 1–37；缺失 24.7% |
| `SecretCode` | 黑客松是否设有密码 | 0：140；1：107 |
| `Country_ID` | 比赛主办国家或黑客松举办地（脱敏方式与 Users 表的国家相同） | 20 个；缺失 51.0% |
| `Start Time time / Year / Month / Day_of_month` | 比赛开始时间 | Year 1–5；Month 1–12 |
| `End Time time / Year / Month / Day_of_month` | 比赛结束时间 | Year 1–5，另有 1 条为 2023；Month 1–12；缺失 9.3% |

---

## 7. Blogs.csv：博客（官方未定义）

| 列 | 字面含义 | 取值 |
|---|---|---|
| `blog_ID` | 博客 ID | 117 个，无重复 |
| `Theme` | 主题 | 1：23；2：42；3：13；4：21；5：15；缺失 3 条 |
| `Published At time / Year / Month / Day_of_month` | 发布时间 | Year 1–5；Month 1–12 |

---

## 8. Jobs.csv：职位（官方未定义）

| 列 | 字面含义 | 取值 |
|---|---|---|
| `job_ID` | 职位 ID | 34 个，无重复 |
| `Remote` | 是否远程 | True：8；False：1；缺失 25 |
| `Experience` | 经验要求（年） | `<1`：6；`1-2`：5；`2-5`：14；`>5`：7；缺失 2 |
| `Industry` | 行业（集合形式，如 `{Government,Health,"Financial Services"}`） | 18 种组合；缺失 5 |
| `Employment Type` | 雇佣类型 | fulltime：20；internship：7；contract：3；parttime：1；缺失 3 |
| `Company Size` | 公司规模（人） | `1-10`：4；`10-50`：10；`50-200`：10；`>200`：5；缺失 5 |
| `Data Science Functions` | 数据科学职能（集合形式，如 `{"Data modelling","Business/Data Analysis"}`） | 21 种组合；缺失 5 |

---

## 9. SampleSubmission.csv：提交样例

| 列 | 含义 | 取值 |
|---|---|---|
| `User_ID_Next_month_Activity` | 用户 ID 加上 `_Month_5` 后缀，如 `ID_4TOXNBGB_Month_5` | 1,340 个 |
| `Active` | 需要预测的值（0 / 1） | 样例中全部为 0 |

---

## 10. VariableDefinitions.csv：官方字段说明

官方字段说明中有一部分在实际数据里不存在：

| 官方说明中的表 / 字段 | 实际数据 |
|---|---|
| Users：`Points`（积分分组，已脱敏） | 不存在 |
| CompetitionParticipation：`PublicRank`（排行榜排名，每 50 名一组，已脱敏） | 不存在 |
| Competitions：`Kind`（比赛还是黑客松）、`Points Reward`（奖励积分，已缩放）、`SubmissionLimitPerDay`（每日提交上限） | 不存在 |
| Submissions 整张表（`CompID`、`FeatureG`、`UserID`、提交时间） | 没有该文件 |

另外，官方说明里的时间字段写的是 `Day_of_week`（星期几），而实际数据中是 `Day_of_month`（几号）；字段名也不完全一致，例如官方写 `UserID`、`Country`，实际数据中是 `User_ID`、`Countries_ID`。
