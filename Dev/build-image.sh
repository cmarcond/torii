imgName="torii-on-prem"
imgVersion="0.0.3"
docker build --label $imgName --tag $imgName:$imgVersion .
docker tag $imgName:$imgVersion secdevias/$imgName:$imgVersion
docker push secdevias/$imgName:$imgVersion
#docker logout
echo "Generating SecDevias-Torii Image....[Done]"
echo "---------------------------------------------------"
echo "| IMAGE secdevias/"$imgName:$imgVersion" - DONE"
echo "---------------------------------------------------"
