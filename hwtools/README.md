# Homework Tools

作业全周期工具。具体使用方法见各模块目录。

使用 [Typer](https://typer.tiangolo.com/) 作为命令行工具。

## Members

### Extract

从教学立方打包的作业中提取各学生的文件。

#### Features

- 处理嵌套解压，支持 zip、7z、rar 格式。能够处理大部分文件名编码问题。
- 忽略评审无关的提交文件，如 VS 的项目、缓存文件。
- 按照 `学号+姓名` 进行归类，并消除嵌套

### Mail

根据批改结果发邮件

#### Features

- 附带分数、评语信息。
- 附件包括

### Review

一键在教学立方提交作业成绩（命令弃用）

## Usage

使用命令行运行：`hwtools <command>`。执行 `hwtools --help` 和 `hwtools <command> --help` 查看命令使用帮助。可利用 VSCode 的 `launch.json` 存储命令并调试。

一些用例：

```sh
hwtools extract path/to/archive.zip --collection path/to/collections --proj proj00 --roster path/to/roster.tsv
hwtools gather path/to/sources
hwtools update-eval --collection path/to/collections --proj proj00
hwtools mail --collection path/to/collections --proj proj00 --roster path/to/roster.tsv --subject "第一次作业"
```

名单为 TSV 格式（制表符分割），需要有如下字段：`一卡通号`、`学号`、`姓名`。

发邮件需要在环境变量设置相关信息（详细见 `EmailSettings` 类），至少包括：

```env
SMTP_USER=your@email.com
SMTP_PASSWORD=123456
SENDER=your@email.com
SENDER_NAME=Your Name
```

作业收集生成的目录结构如下：

```txt
collections
├── proj00
│   ├── collect
│   │   └── 61520000 穹天帝
│   │       ├── file1.h
│   │       └── file1.cpp
│   ├── eval
│   │   └── 61520000 穹天帝
│   │       ├── file1.h
│   │       └── file1.cpp
│   ├── logs
│   └── mails
└── proj01
```
