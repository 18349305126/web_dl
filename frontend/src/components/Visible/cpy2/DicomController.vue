<template>
  <div class="container">
    <!-- <el-form ref="form" :model="form" label-width="120px" style="width: 50%">
      <el-form-item label="保存至文件夹">
        <input type="file" id="file" hidden @change="fileChange" webkitdirectory multiple="multiplt">
        <el-input placeholder="请输入内容" v-model="form.imgSavePath" class="input-with-select">
          <el-button slot="append" icon="el-icon-folder" type="success" @click="btnChange"></el-button>
        </el-input>
      </el-form-item>
    </el-form> -->

    <div class="col-sm-3">
      <!-- <div class="block">
        <span class="demonstration">自定义初始值</span>
        <el-slider v-model="index"></el-slider>
      </div> -->
      <el-slider v-model="z_index" :max="dicoms_num - 1"> </el-slider>

      <input type="file" id="selectFile" multiple="multiplt" />
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
        <DicomWindow
          v-bind:img="img"
          v-bind:width="wnd_w"
          v-bind:height="wnd_h"
        ></DicomWindow>
      </div>
    </div>
  </div>
</template>

<script>
// //引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
import DicomWindow from "./dicomhandle/DicomWindow";
import * as cornerstone from "cornerstone-core";
import * as dicomParser from "dicom-parser";
import * as math from "mathjs";
import * as tf from "@tensorflow/tfjs";

// 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
import * as cornerstoneWADOImageLoader from "../../../static/dist/cornerstoneWADOImageLoader.js";

// Cornerstone 工具外部依赖
import Hammer from "hammerjs";
import * as cornerstoneMath from "cornerstone-math";
import * as cornerstoneTools from "cornerstone-tools";
import { dot } from "mathlab";
import { Tensor } from "@tensorflow/tfjs";

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
      //窗口参数的设置
      wnd_w: "512px",
      wnd_h: "512px",

      //dicom文件的数据
      dicoms: "", //存储所有dicom文件
      dicoms_num: Number,
      x_len: Number,
      // x_len: "",

      y_len: Number,
      z_len: Number,
      dicom: "", //当下展示的dicom文件
      imgs: "", //所有dicom文件对应的图像
      img: "", //当前的dicom图像

      x_mats:"",
      x_mat:"",

      z_index: Number, //当前的dicom文件座标
      x_index: Number,
      y_index: Number,
      raw: "", //三维数据场
      read_num: Number, //表示当前异步读取文件数
      finished: Boolean, //判断图像是否加载完成
    };
  },
  created() {
    // this.x_len = 0;
    // this.y_len = 0;
    this.finished = false;
    this.read_num = 0;
    this.z_index = 0;
    this.dicoms_num = 1;
  },
  mounted() {
    //与dom有关的操作在mounted
    // this.imgs=new Array();
    //挂载选择文件功能
    // console.log("dicom", this.dicom);

    document
      .getElementById("selectFile")
      .addEventListener("change", this.handleFileSelect);
  },
  methods: {
    handleFileSelect(evt) {
      // console.log(111);

      evt.stopPropagation();
      evt.preventDefault();
      this.dicoms = evt.target.files;
      const dicom = evt.target.files[0];
      this.imgs = new Array(this.dicoms.length);
      // console.log("imgs",this.imgs);
      this.dicoms_num = this.dicoms.length;
      this.z_len = this.dicoms_num;

      this.dicom = dicom;

      for (let i = 0; i < this.dicoms.length; i++) {
        // const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(this.dicoms[i]);
        this.appendImg(this.dicoms[i], i);
      }

      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(dicom);
      this.getImg(imageId);
    },
    getImg(imageId) {
      const _this = this;
      // let img;
      cornerstone.loadAndCacheImage(imageId).then(
        function (image) {
          _this.img = image;
        },
        function (err) {
          alert(err);
        }
      );
    },
    appendImg(dcm, z_idx) {
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(dcm);
      const _this = this;
      cornerstone.loadAndCacheImage(imageId).then(
        function (image) {
          // if (_this.x_len < 0) {
          //   _this.x_len = image.width;
          //   _this.y_len = image.height;
          //   console.log(_this.x_len);
          // }
          _this.x_len = image.width;
          _this.y_len = image.height;
          // console.log(_this.x_len);

          _this.imgs[z_idx] = image;
          _this.read_num++;
          if (_this.read_num == _this.z_len) {
            _this.finished = true;
            console.log("加载完成");
          }
          // console.log(_this.imgs);
        },
        function (err) {
          alert(err);
        }
      );
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
      let style = this.StringFormat(
        "width: {0};height: {1};position: relative;color: white;display: inline-block;border-style: solid;border-color: black;",
        this.wnd_w,
        this.wnd_h
      );

      // console.log(style);
      return style;
    },
    judgeEmpty(array) {
      let len = array.length;
      for (let i = 0; i < len; i++) {
        if (array[i] == undefined) {
          return false;
        }
      }
      return true;
    },
    reshape(array, wid, height) {
      let Mat = new Array();
    },
    rebuild3D(images) {//默认dicom文件间的像素也为1
      console.log(this.imgs[0]);
      // this.raw = tf.zeros([this.x_len, this.y_len, this.z_len]);
      let raw =  tf.reshape(tf.tensor(Array.from(images[0].getPixelData())), [this.x_len, this.y_len,1]);

      for (let i = 1; i < this.z_len; i++) {
        // console.log(raw);
        // console.log(Array(images[i].getPixelData()));
        let data = tf.tensor(Array.from(images[i].getPixelData()));
        // console.log(data.shape);
        data = tf.reshape(data, [this.x_len, this.y_len,1]);
        raw = tf.concat([raw, data],2);

      }
      this.raw=raw;
      // console.log(raw);
    },
  },
  watch: {
    img(new_img, old_img) {
      // if(this.x_len=undefined || this.y_len=undefined){
      // }
      // console.log("new_img",new_img);
    },
    imgs(new_imgs, old_imgs) {
      // console.log("new_imgs",new_imgs);
      this.img = this.imgs[0];
      // console.log("是否完成",this.judgeEmpty(this.imgs),this.imgs);
      // console.log(this.img);
    },
    z_index(new_id, old_id) {
      this.img = this.imgs[new_id];
      if (this.img != undefined && new_id >= 0) {
        // console.log("img", this.img, new_id);
        // console.log(this.img.getPixelData());
      }
    },
    finished(new_f, old_f) {
      if (new_f) {
        this.rebuild3D(this.imgs);
      }
    },
  },
};
</script>