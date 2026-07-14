@echo off
echo ==================================
echo  代理命令行测试
echo ==================================
echo.
echo [测试] 通过代理访问 ipinfo.io...
curl -x http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091 ipinfo.io
echo.
echo ==================================
echo  如果能显示IP信息，代理可用
echo  如果报错，请检查代理配置
echo ==================================
pause
