<template>
  <div class="container">
    <div class="col-sm-3">
      <input type="file" id="selectFile" />
    </div>
    <div class="col-md-6">
      <!-- <div
        style="
          width: 512px;
          height: 512px;
          position: relative;
          color: white;
          display: inline-block;
          border-style: solid;
          border-color: black;
        "
        oncontextmenu="return false"
        class="disable-selection noIbar"
        unselectable="on"
        onselectstart="return false;"
        onmousedown="return false;"
      >
      <DicomWindow></DicomWindow>
        
      </div> -->
      <div v-bind:style="getStyle()">
        <DicomWindow v-bind:file='file'></DicomWindow>
      </div>
    </div>
  </div>
</template>

<script>
// //引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
import DicomWindow from "./dicomhandle/DicomWindow";
import * as cornerstone from "cornerstone-core";
import * as dicomParser from "dicom-parser";

// 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
import * as cornerstoneWADOImageLoader from "../../../static/dist/cornerstoneWADOImageLoader.js";

// Cornerstone 工具外部依赖
import Hammer from "hammerjs";
import * as cornerstoneMath from "cornerstone-math";
import * as cornerstoneTools from "cornerstone-tools";

// Specify external dependencies
cornerstoneTools.external.Hammer = Hammer;
cornerstoneTools.external.cornerstone = cornerstone;
cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath;

//指定要注册加载程序的基石实例
cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

cornerstone.registerImageLoader("http", cornerstoneWADOImageLoader.loadImage);
cornerstone.registerImageLoader("https", cornerstoneWADOImageLoader.loadImage);

//配置 webWorker (必须配置)
//注意这里的路径问题  如果路径不对 cornerstoneWADOImageLoaderWebWorker 会报错 index.html Uncaught SyntaxError: Unexpected token <
var config = {
  webWorkerPath: "/static/dist/cornerstoneWADOImageLoaderWebWorker.js",
  taskConfiguration: {
    decodeTask: {
      codecsPath: "/static/dist/cornerstoneWADOImageLoaderCodecs.js",
    },
  },
};
if (!cornerstoneWADOImageLoader.webWorkerManager.config) {
  // console.log(cornerstoneWADOImageLoader.webWorkerManager.config);
  cornerstoneWADOImageLoader.webWorkerManager.initialize(config);
}

export default {
  name: "DicomController",
  components: { DicomWindow },
  // props:["flie"],
  data() {
    return {
      wnd_w: "512px",
      wnd_h: "512px",
      file: "",
      // test_data:"",
    };
  },
  mounted () {
    //挂载选择文件功能
    document.getElementById("selectFile").addEventListener("change",this.handleFileSelect);
  },
  methods: {
    handleFileSelect(evt) {
      // console.log(111);
      evt.stopPropagation();
      evt.preventDefault();
      const file = evt.target.files[0];
      this.file = file;

      // console.log(this.file);

    //   const files = evt.dataTransfer.files;
    //   file = files[0];

      // const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
      // // console.log("imageId:", imageId);
      // this.loadAndViewImage(imageId);
    },
    StringFormat() {
      if (arguments.length == 0) return null;
      var str = arguments[0];
      for (var i = 1; i < arguments.length; i++) {
        var re = new RegExp("\\{" + (i - 1) + "\\}", "gm");
        str = str.replace(re, arguments[i]);
      }
      return str;
    },
    getStyle() {
      let style = this.StringFormat("width: {0};height: {1};position: relative;color: white;display: inline-block;border-style: solid;border-color: black;",this.wnd_w,this.wnd_h);
      
      // console.log(style);
      return style;
    },
  },
};
</script>