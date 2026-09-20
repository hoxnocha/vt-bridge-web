# VT-Bridge 项目网页

这个仓库维护 VT-Bridge 的静态项目网页。研究代码在独立仓库中维护。

## 目录

```text
.
├── index.html          # 项目主页、方法介绍和结果
├── styles.css          # 页面样式与响应式布局
├── script.js           # 视频选择、播放控制及引用复制
├── video-data.js       # 视频展示所用的数据
├── video-library.html  # 录制视频的备用索引页
├── assets/             # 页面使用的图片、视频、字体和论文
├── .nojekyll           # GitHub Pages 直接提供静态文件
└── README.md
```

## 本地预览

直接用 Firefox 打开仓库根目录的 `index.html`。网页无需安装依赖或启动后端。

如果需要通过本地 HTTP 地址检查页面，在仓库根目录执行：

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

然后访问 `http://127.0.0.1:8000/`。

## 更新页面

- 编辑 `index.html` 中的项目内容，编辑 `styles.css` 调整样式。
- 媒体文件放在 `assets/` 中，保持相对路径。视频展示数据在 `video-data.js` 中。
- 保留 `.nojekyll`，并在提交前检查页面、图片和视频能否正常打开。
- 仓库只保存网页需要的文件；训练代码、模型权重和完整数据集单独管理。

如果继续使用已有的 `project-page` 工作目录及其发布脚本，将生成的 `dist/` **内部文件**同步到此仓库根目录，不要再包一层 `vt-bridge-private/` 或 `dist/`。

## 视频按需加载

页面先显示封面，点击 Play video 后才把原始视频地址交给播放器。切换 backbone 或相机视角时，旧播放器会停止并释放资源，新选项仍需点击播放。实验、ablation 对比和额外分析录像使用相同逻辑；全部原始录像保持不变。

新增额外分析录像时，沿用 `index.html` 中的 `video[data-src]` 写法，提供封面和 `<noscript>` 直达链接；不要添加会提前加载的 `src` 或 `<source src>`。图库录像继续在 `video-data.js` 中配置。此功能减少访问时下载的视频量，不减少仓库或部署文件的总大小。

## GitHub Pages

网页文件位于 `main` 根目录。决定公开时，可在 GitHub 仓库的 **Settings → Pages** 中选择 **Deploy from a branch → main → / (root)**。

推送代码、仓库可见性和网站发布是不同操作；整理目录不会自动更改仓库可见性或启用 Pages。网站一旦配置为从 `main` 发布，后续推送到该分支会触发更新。

当前页面中尚未补齐的项目元数据应根据论文和实际代码仓库填写。

## 访问计数

页脚右侧使用 [Hits.sh](https://github.com/silentsoft/hits) 显示所有访问者共享的累计访问次数（并非独立访客人数）。网站通过 HTTPS 发布到 `*.github.io` 后自动启用，无需后端或 API 密钥；点击计数徽章可查看统计。计数从启用后开始，无法恢复此前的访问量。

本地预览显示 `Visits —`，不向计数服务发送请求。统计标识使用发布页面的域名和路径，不包含查询参数或锚点；目录地址与 `index.html` 共用计数。若服务不可用，显示 `Visits unavailable`。如将来改用自定义域名，需更新 `script.js` 中的域名检查，并决定是否沿用原计数标识。

## 方法架构图

架构图由 Graphviz 生成。安装 Graphviz 后，在仓库根目录运行：

```bash
python3 tools/render_method_diagrams.py
```

编辑脚本中的节点和连接可同步生成桌面与手机版的 `.gv` 源文件及 `.svg` 图片，输出在 `assets/diagrams/`。网页直接显示 SVG，浏览器无需安装 Graphviz。图中的特征小格是示意，不表示具体隐藏维度或网络层数；网络连接依据论文的方法部分。
