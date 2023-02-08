#/bin/bash

# cd ./bilateral_kernels
# ./bilateral_kernels.sh
# cd ../

scenes=( "arcade_anim" "bistro_anim" "bistro2_anim" "bistroWine_anim" "suntemple_anim" "zeroday_anim" )

for scene in "${scenes[@]}"; do
   for i in {0..100}
   do
      python network_test.py -r /dataset_falcor -d $scene --export_exr -ts 100 -t $i
      mkdir -p output/$scene
      mv $scene/result/test_out/* output/$scene
   done
done

# python network_test.py -r ./dataset -d classroom --export_exr --export_guide_weight -ts 60 -t 0