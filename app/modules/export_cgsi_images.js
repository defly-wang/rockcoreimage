/**
 * 在浏览器控制台运行此代码，复制输出的JSON
 */
(function() {
    var images = [];
    var rows = typeof ystxRows !== 'undefined' ? ystxRows : [];
    
    rows.forEach(function(item, idx) {
        images.push({
            start_depth: item.QSSD,
            end_depth: item.ZZSD,
            yxtpbh: item.YXTPBH,
            dzms: item.DZMS || '',
            height: item.HD
        });
    });
    
    console.log('岩心图片数据 (%d 张):', images.length);
    console.log(JSON.stringify(images, null, 2));
})();
