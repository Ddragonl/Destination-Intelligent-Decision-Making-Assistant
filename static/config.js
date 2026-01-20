// 高德地图Web API配置
// 注意：这里需要配置你的高德地图Web API Key
// 获取方式：https://lbs.amap.com/api/javascript-api/guide/abc/prepare
// 在控制台创建应用，选择"Web端(JS API)"

// 如果不想在这里配置，可以在index.html中直接替换YOUR_AMAP_WEB_KEY
const AMAP_WEB_KEY = 'YOUR_AMAP_WEB_KEY';

// 导出配置（如果使用模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AMAP_WEB_KEY };
}

