#/bin/bash

# cd ./bilateral_kernels
# ./bilateral_kernels.sh
# cd ../

for i in {0..100}
do
#    python network_test.py -r /dataset_falcor -d arcade_anim --export_exr --export_guide_weight -ts 100 -t $i
   python network_test.py -r /dataset_falcor -d arcade_anim --export_exr -ts 100 -t $i
#    python network_test.py -r /dataset_falcor -d arcade_anim -ts 100 -t $i
done


# python network_test.py -r ./dataset -d classroom --export_exr --export_guide_weight -ts 60 -t 0