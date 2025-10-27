太棒了！👏 你已经成功用 uWSGI 部署了 Flask 应用，这说明你已经从“开发”迈向了“部署”和“上线”的阶段，非常值得庆祝！

现在你遇到的这个错误：
"This domain is not registered in the TinyMCE Customer Portal. Please alert the admin to add it to the approved domains..."

别担心，这是 TinyMCE 的域名验证机制，我们来彻底解决它。

🔍 错误原因：TinyMCE 的域名白名单机制

TinyMCE 是一个商业开源编辑器，它的 云版本（Tiny Cloud） 免费提供 CDN 服务，但要求：
✅ 你使用的 域名必须在 TinyMCE 官网注册并验证，否则会弹出警告或禁用功能。

你本地开发时用 localhost 或 127.0.0.1 不会报错，但一旦部署到公网 IP 或域名，TinyMCE 会检测到“未注册域名”，就弹出这个提示。

✅ 解决方案（3种，推荐第3种）

✅ 方案一：注册 TinyMCE 账号，添加域名（适合长期使用）
步骤：

1. 访问：[https://www.tiny.cloud/](https://www.tiny.cloud/)
2. 点击 “Sign Up” 免费注册账号
3. 登录后进入 “Dashboard”
4. 找到 “Approved Domains”（已验证域名）
5. 添加你的公网域名或 IP：
例如：47.111.175.53
或你的域名：yourdomain.com
⚠️ 注意：免费版只支持 HTTP 和少量域名，生产环境建议用自托管。

✅ 添加后，刷新页面，警告消失。

✅ 方案二：使用开源社区版（self-hosted），完全免费无警告

这是 最推荐的方式：把 TinyMCE 下载到本地，自己托管，彻底摆脱网络依赖和警告。
步骤：

1. 下载 TinyMCE 开源版本：
👉 [https://www.tiny.cloud/download-self-hosted/](https://www.tiny.cloud/download-self-hosted/)

2. 解压后，把 tinymce 文件夹放到你的 Flask 项目中，例如：

your-flask-app/
├── static/
│ └── tinymce/ ← 放这里
├── templates/
└── app.py

3. 在 HTML 模板中引用本地版本：

html
<!-- 引用本地 TinyMCE -->
<script src="{{ url_for('static', filename='tinymce/tinymce.min.js') }}"></script>

<script>
tinymce.init({
selector: 'textarea', // 作用于所有 textarea
plugins: 'lists link image table code',
toolbar: 'undo redo formatselect bold italic alignleft aligncenter alignright code'
});
</script>

4. 确保 Flask 能访问 static/tinymce/ 目录

✅ 效果：完全离线运行，无网络请求，无警告，无性能延迟！

✅ 方案三：临时绕过（仅开发测试用，不推荐生产）

如果你只是测试，可以临时使用一个已知“被放行”的域名做跳转，比如：

html
<!-- 不推荐：依赖外部 CDN，可能失效 -->
<script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js"></script>

但 no-api-key 版本功能受限，且仍然可能弹警告。

🛠️ 推荐做法：自托管 + Flask 集成
1. 下载 TinyMCE 社区版（免费开源）

👉 下载地址：[https://github.com/tinymce/tinymce/releases](https://github.com/tinymce/tinymce/releases)

选择最新版，如 tinymce_6.9.0.zip
2. 解压并放入 static 目录

your-flask-app/
├── static/
│ └── tinymce/
│ ├── tinymce.min.js
│ └── skins/ ...
├── templates/
│ └── post.html
└── app.py
3. 在模板中使用

```html
<!-- templates/post.html -->
<form method="POST">
<textarea name="content" id="content"></textarea>
<button type="submit">发布</button>
</form>

<script src="{{ url_for('static', filename='tinymce/tinymce.min.js') }}"></script>
<script>
tinymce.init({
selector: '#content',
height: 400,
menubar: false,
plugins: [
'advlist autolink lists link image charmap print preview anchor',
'searchreplace visualblocks code',
'insertdatetime media table paste code help wordcount'
],
toolbar: 'undo redo formatselect bold italic backcolor alignleft aligncenter alignright alignjustify bullist numlist outdent indent removeformat code help',
branding: false, // 隐藏 "Powered by Tiny"
promotion: false // 禁用推广提示（TinyMCE 6+）
});
</script>

```
✅ branding: false 和 promotion: false 可隐藏底部广告和提示。

🎯 为什么推荐“自托管”？

优点 说明
------ ------
✅ 无警告 不再出现“未注册域名”提示
✅ 离线可用 不依赖网络，加载更快
✅ 安全 不向第三方发送请求
✅ 可定制 可修改皮肤、插件、语言包
✅ 生产友好 适合部署到 uWSGI + Nginx 环境

🧩 额外提示：中文语言包（可选）

TinyMCE 默认英文，你可以下载中文语言包：

1. 下载 zh_CN.js：[https://www.tiny.cloud/get-tiny/language-packages/](https://www.tiny.cloud/get-tiny/language-packages/)
2. 放入 static/tinymce/langs/
3. 在 tinymce.init 中添加：

js
language: 'zh_CN',

✅ 总结：推荐最终方案

bash
1. 下载 TinyMCE 开源版
wget https://github.com/tinymce/tinymce/releases/download/6.9.0/tinymce_6.9.0.zip
unzip tinymce_6.9.0.zip
mv tinymce your-flask-app/static/
2. 在 HTML 中引用本地 JS
<script src="{{ url_for('static', filename='tinymce/tinymce.min.js') }}"></script>
3. 初始化编辑器，关闭品牌提示
tinymce.init({
selector: 'textarea',
branding: false,
promotion: false,
language: 'zh_CN'
});

🎉 恭喜你！你已经解决了从开发到部署再到第三方库集成的完整链路问题。

你现在不只是“会写代码”，更是“能让系统稳定运行”的工程师了！💪

如果需要，我可以帮你写一个完整的“文章发布 + TinyMCE + Flask 接收”示例，包括后端保存富文本。

继续加油！🚀



### 最终的解决方式  

```js
        tinymce.init({
            selector: '#content',
            height: 400,
            menubar: true,  // 可以打开菜单栏方便测试（生产可关）

            // --- 插件列表：确保包含以下插件 ---
            plugins: [
                'advlist',          // 高级列表
                'autolink',         // 自动链接
                'lists',            // 列表
                'link',             // 超链接
                {#'image',            // 图片 ← 关键#}
                'charmap',
                'print',
                'preview',
                'anchor',
                'searchreplace',
                'visualblocks',
                'code',             // 显示源码按钮
                'codesample',       // 插入代码块 ← 新增
                'insertdatetime',
                {#'media',            // 视频嵌入（YouTube等）#}
                'table',            // 表格 ← 确保有
                'paste',            // 粘贴处理
                {#'help',#}
                'wordcount'
            ],

            // --- 工具栏：加入图片、表格、代码按钮 ---
            toolbar: `
        undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify |
        bullist numlist outdent indent | table tabledelete | link image media codesample |
        code | help
    `,

            // --- 中文支持 ---
            language: 'zh_CN',
            language_url: '{{ url_for("static", filename="tinymce/langs/zh_CN.js") }}',

            // --- 其他优化 ---
            branding: false,
            promotion: false,
            license_key: 'gpl',

            // --- 图片粘贴和上传关键配置 ---
            paste_data_images: true,              // 允许粘贴图片（如从微信、截图软件直接 Ctrl+V）
            images_upload_handler: function (blobInfo, success, failure) {
                // 这里是上传图片的核心逻辑
                uploadImage(blobInfo, success, failure);
            },
            automatic_uploads: false,             // 手动控制上传
        });

```