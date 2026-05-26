def get_map_html(sel_floor, sel_p_floor, h_b64, p_b64):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; font-family: "Microsoft JhengHei", sans-serif; background-color: transparent; overflow: hidden; }}
            .label {{ font-size: 16px; font-weight: bold; color: #333; margin: 10px 0 5px 0; }}
            .viewport {{ width: 100%; height: 350px; background: #fafafa; border: 1px solid #e1e4e8; border-radius: 12px; position: relative; overflow: hidden; cursor: grab; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 15px; }}
            .viewport:active {{ cursor: grabbing; }}
            .img-container {{ position: absolute; transform-origin: 0 0; user-select: none; -webkit-user-drag: none; }}
            .img-container img {{ width: 100%; height: auto; display: block; -webkit-user-drag: none; pointer-events: none; }}
        </style>
    </head>
    <body>
        <div class="label">🏠 房屋：{sel_floor} 平面圖 (滑鼠按著可任意拖曳 / 滾輪可放大縮小)</div>
        <div id="vp1" class="viewport"><div id="box1" class="img-container"><img id="img1" src="{h_b64}"></div></div>
        
        <div class="label">🚗 車位：{sel_p_floor} 平面圖 (滑鼠按著可任意拖曳 / 滾輪可放大縮小)</div>
        <div id="vp2" class="viewport"><div id="box2" class="img-container"><img id="img2" src="{p_b64}"></div></div>

        <script>
            function setupPanZoom(vpId, boxId, imgId, b64) {{
                const vp = document.getElementById(vpId);
                const box = document.getElementById(boxId);
                const img = document.getElementById(imgId);
                if (!b64) {{ vp.innerHTML = "<div style='text-align:center; line-height:350px; color:#999;'>💡 暫無此樓層平面圖檔</div>"; return; }}

                let scale = 1, pointX = 0, pointY = 0, startX = 0, startY = 0, isPanning = false;
                img.onload = function() {{
                    box.style.width = (vp.clientWidth * 0.9) + "px";
                    pointX = (vp.clientWidth - box.clientWidth) / 2;
                    pointY = (vp.clientHeight - (box.clientWidth * (img.naturalHeight / img.naturalWidth))) / 2;
                    update();
                }};
                if(img.complete) img.onload();
                function update() {{ box.style.transform = `translate(${{pointX}}px, ${{pointY}}px) scale(${{scale}})`; }}

                vp.onwheel = function (e) {{
                    e.preventDefault();
                    const xs = (e.clientX - vp.getBoundingClientRect().left - pointX) / scale;
                    const ys = (e.clientY - vp.getBoundingClientRect().top - pointY) / scale;
                    if (e.deltaY < 0) {{ scale *= 1.15; }} else {{ scale /= 1.15; }}
                    scale = Math.min(Math.max(0.5, scale), 8);
                    pointX = e.clientX - vp.getBoundingClientRect().left - xs * scale;
                    pointY = e.clientY - vp.getBoundingClientRect().top - ys * scale;
                    update();
                }};
                vp.onmousedown = function (e) {{ e.preventDefault(); startX = e.clientX - pointX; startY = e.clientY - pointY; isPanning = true; }};
                window.onmousemove = function (e) {{ if (!isPanning) return; pointX = e.clientX - startX; pointY = e.clientY - startY; update(); }};
                window.onmouseup = function (e) {{ isPanning = false; }};
            }}
            setupPanZoom("vp1", "box1", "img1", "{h_b64}");
            setupPanZoom("vp2", "box2", "img2", "{p_b64}");
        </script>
    </body>
    </html>
    '''
