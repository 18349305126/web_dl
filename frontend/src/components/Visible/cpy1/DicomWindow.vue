<template>
  <div>
    <div
      id="dicomImage"
      style="
        width: 512px;
        height: 512px;
        top: 0px;
        left: 0px;
        position: absolute;
      "
    ></div>
    <!-- <input id="test" type ="button" style="position: absolute;"/> -->
  </div>
</template>

<script>
//引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
import * as cornerstone from "cornerstone-core";
import * as dicomParser from "dicom-parser";

// 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
import * as cornerstoneWADOImageLoader from "../../../../static/dist/cornerstoneWADOImageLoader.js";

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
if (!cornerstoneWADOImageLoader.webWorkerManager.config)
  cornerstoneWADOImageLoader.webWorkerManager.initialize(config);

export default {
  name: "DicomWindow",
  props: ["file"],
  data() {
    return {
      // file: "",
      img:"",
      // test_data:"",
    };
  },
  methods: {
    test(evt){
      // console.log("hello test");
      console.log("test",this.test_data);
    },
    
    handleFileSelect(evt) {
      console.log(111);
      evt.stopPropagation();
      evt.preventDefault();
      const file = evt.target.files[0];

      //   const files = evt.dataTransfer.files;
      //   file = files[0];
      // console.log("flie:", flie);
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
      // console.log("imageId:", imageId);
      this.loadAndViewImage(imageId);
    },

    // handleDragOver(evt) {
    //   evt.stopPropagation();
    //   evt.preventDefault();
    //   evt.dataTransfer.dropEffect = "copy"; // Explicitly show this is a copy.
    // },
    loadAndViewImage(imageId) {
      const _this = this;
      //找到 要放置 Dicom Image 的元素
      var element = document.getElementById("dicomImage");
      // cornerstone.loadAndCacheImage 函数 负责加载图形 需要 图像地址 imageId
      // console.log("imageid",imageId);
      cornerstone.loadAndCacheImage(imageId).then(
        function (image) {
          // console.log("image",image);
          // this.image = image;
          _this.img = image;
          // _this.test_data = 10;
          var viewport = cornerstone.getDefaultViewportForImage(element, image);
          cornerstone.displayImage(element, image, viewport);
        },
        function (err) {
          alert(err);
        }
      );
      // console.log("thisimg",_this.img)
    },
  },
  mounted() {
    let element = document.getElementById("dicomImage");
    cornerstone.enable(element);
    

    document.getElementById("test").addEventListener("click",this.test);
    // console.log(document.getElementById("test"));
    // document
    //   .getElementById("selectFile")
    //   .addEventListener("change", this.handleFileSelect);
  },
  watch: {
    file(new_file, old_file) {
      // console.log("new file", new_file);
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(new_file);
      // console.log("imageId:", imageId);
      this.loadAndViewImage(imageId);

    },
    img(new_img,old_img){
      console.log("new_img",new_img);
    },
    // test_data(new_data, old_data) {
    //   console.log("new_data", new_data);
    //   console.log("old_data", old_data);
    // },
    
  },
};
</script>