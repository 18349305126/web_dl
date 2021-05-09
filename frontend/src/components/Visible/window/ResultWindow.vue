<template>
  <!-- <div>
    <div v-if="result_wnd_state == 1">
      <FusionWindow
        label="z"
        v-bind:mat0="mat0"
        v-bind:mat1="mat1"
        v-bind:mat2="mat2"
        v-bind:width="width"
        v-bind:height="height"
        v-bind:mat0_row_spacing="mat0_row_spacing"
        v-bind:mat0_col_spacing="mat0_col_spacing"
        v-bind:fusion_states="fusion_states"
      >
      </FusionWindow>
    </div>

    <div v-else-if="result_wnd_state == 2">

    </div>
    
    <div v-else>
      <VolumeRenderWindow
        v-bind:width="width"
        v-bind:height="height"
        >
      </VolumeRenderWindow>
    </div>


  </div> -->
  <div>
    <div v-if="this.$store.getters.result_view_state == 1">
      <FusionWindow
        label="z"
        v-bind:mat0="mat0"
        v-bind:mat1="mat1"
        v-bind:mat2="mat2"
        v-bind:width="width"
        v-bind:height="height"
        v-bind:mat0_row_spacing="mat0_row_spacing"
        v-bind:mat0_col_spacing="mat0_col_spacing"
      >
      </FusionWindow>
    </div>

    <div v-else-if="this.$store.getters.result_view_state == 2">
      <LabelWindow
        label="z"
        v-bind:mat="label_mat"
        v-bind:marks="marks"
        v-bind:width="width"
        v-bind:height="height"
        v-bind:mat_row_spacing="mat0_row_spacing"
        v-bind:mat_col_spacing="mat0_col_spacing"
      >

      </LabelWindow>
    </div>
    
    <div v-else>
      <VolumeRenderWindow
        v-bind:width="width"
        v-bind:height="height"
        
        v-bind:vers = "vers"
        v-bind:normals = "normals"
        >
      </VolumeRenderWindow>
    </div>


  </div>
</template>

<script>
import FusionWindow from "./FusionWindow";
import VolumeRenderWindow from "./VolumeRenderWindow";
import LabelWindow from "./LabelWindow";
import * as tf from "@tensorflow/tfjs";
import * as THREE from "three";

// //引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
// import * as cornerstone from "cornerstone-core";
// import * as dicomParser from "dicom-parser";

// // 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
// import * as cornerstoneWADOImageLoader from "../../../../static/dist/cornerstoneWADOImageLoader.js";

// // Cornerstone 工具外部依赖
// import Hammer from "hammerjs";
// import * as cornerstoneMath from "cornerstone-math";
// import * as cornerstoneTools from "cornerstone-tools";
// var c = require("../../../../static/opencvjs/opencv_js.js");

// // Specify external dependencies
// cornerstoneTools.external.Hammer = Hammer;
// cornerstoneTools.external.cornerstone = cornerstone;
// cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
// cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath;

// //指定要注册加载程序的基石实例
// cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

// cornerstone.registerImageLoader("http", cornerstoneWADOImageLoader.loadImage);
// cornerstone.registerImageLoader("https", cornerstoneWADOImageLoader.loadImage);

// //配置 webWorker (必须配置)
// //注意这里的路径问题  如果路径不对 cornerstoneWADOImageLoaderWebWorker 会报错 index.html Uncaught SyntaxError: Unexpected token <
// var config = {
//   webWorkerPath: "/static/dist/cornerstoneWADOImageLoaderWebWorker.js",
//   taskConfiguration: {
//     decodeTask: {
//       codecsPath: "/static/dist/cornerstoneWADOImageLoaderCodecs.js",
//     },
//   },
// };
// if (!cornerstoneWADOImageLoader.webWorkerManager.config)
//   cornerstoneWADOImageLoader.webWorkerManager.initialize(config);

export default {
  name: "DicomResultWindow",
  components: { FusionWindow,VolumeRenderWindow,LabelWindow},

  props: [
    "mat0",
    "mat1",
    "mat2",

    "width",
    "height",

    "mat0_row_spacing",
    "mat0_col_spacing",

    "mat1_row_spacing",
    "mat1_col_spacing",

    "mat2_row_spacing",
    "mat2_col_spacing",

    "label",

    "vers",
    "normals",

    "label_mat",
    "marks"

  ],
  //其中mat是dicomController传过来的切片矩阵，
  //width,heigth是针对dom元素的长宽
  //mat_width，mat_height是mat的宽度高度
  //mat_row_spacing,mat_col_spacing是原dicom文件中像素距离，可以看作渲染时的缩放倍数
  //state为0时表示无任何数据，state为1时表示三维显示，state为2时表示图像融合
  data() {
      return {}
  },
  mounted() {    
    this.init();
  },
  methods: {
    init() {
    },
  },
  watch:{
    "$store.state.visible.result_view_state"(new_state){
      // console.log(new_state)
      // console.log(this.mat0,this.mat1);
      
    },
    label_mat(new_m){
    }
    // vers(new_v){
    //   console.log(new_v);
    // },
    // normals(new_n){
    //   console.log(new_n)
    // }
  }
};
</script>