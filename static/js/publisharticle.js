$(function() {
    // 设置富文本
    tinymce.init({
        selector: '.mytextarea',
        height: 400,
        plugins: 'quickbars emoticons lists link image code table',
        inline: false,
        toolbar: true,  // 使用默认工具栏
        menubar: true,  // 使用默认菜单栏
        cloud_channel: '6', // 使用 TinyMCE 6 稳定版
        // 可选：自定义工具栏
        // toolbar: 'undo redo | blocks | bold italic | alignleft aligncenter alignright | link image | code',
        quickbars_selection_toolbar: 'bold italic | link h2 h3 blockquote',
        quickbars_insert_toolbar: 'quickimage quicktable',
        wordcount: true,
        language:"zh_CN"
    });
});