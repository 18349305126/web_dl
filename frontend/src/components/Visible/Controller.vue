<template>
  <div class="container">
    <div class="col-md-6">
      <el-row :gutter="10">
        <el-col :span="12" style="text-align: center">
          <h3 style="margin: 0; line-height: 30px">
            窗口0
            <!-- <el-switch
              v-model="magnifying"
              active-icon-class="el-icon-zoom-in"
              inactive-icon-class="el-icon-circle-close"
            >
            </el-switch> -->
          </h3>

          <div v-bind:style="getStyle2()">
            <!-- <el-button type="primary" icon="el-icon-view"></el-button> -->

            <!-- <input type="file" id="dicom_flies0" multiple="multiplt" placeholder="本地dicom文件上传"/> -->
            <div>
              <VisibleWindow
                v-bind:label="labels[0]"
                v-bind:p_mat="mats0"
                v-bind:width="wnd_w"
                v-bind:height="wnd_h"
                v-bind:mat_row_spacing="pix_row_spacings[0]"
                v-bind:mat_col_spacing="pix_col_spacings[0]"
              ></VisibleWindow>
            </div>
            <el-slider v-model="z_index" :max="this.lens[0] - 1" show-input>
            </el-slider>
          </div>
        </el-col>
        <el-col
          v-loading="loading_vers_normals"
          element-loading-text="后台正在快马加鞭处理，请稍等！"
          element-loading-background="rgba(0, 0, 0, 0.8)"
          :span="12"
        >
          <h3 style="margin: 0; line-height: 30px">结果窗口</h3>
          <div v-bind:style="getStyle2()">
            <!-- <el-slider v-model="x_index" :max="this.lens[1] - 1" show-input>
            </el-slider> -->

            <!-- <input type="file" id="selectFile" multiple="multiplt" /> -->
            <!-- <input type="file" id="dicom_flies1" multiple="multiplt" placeholder="本地dicom文件上传"/> -->
            <div>
              <ResultWindow
                label="z"
                v-bind:mat0="result_mats[0]"
                v-bind:mat1="result_mats[1]"
                v-bind:mat2="result_mats[2]"
                v-bind:width="wnd_w"
                v-bind:height="wnd_h"
                v-bind:mat0_row_spacing="pix_row_spacings[0]"
                v-bind:mat0_col_spacing="pix_col_spacings[0]"
                v-bind:vers="vers"
                v-bind:normals="normals"
                v-bind:label_mat="label_mat"
                v-bind:marks="marks"
                v-bind:z_index="z_index - lens[0] / 2"
                v-bind:x_index="x_index - lens[1] / 2"
                v-bind:y_index="y_index - lens[2] / 2"
                v-bind:z_mat="z_mat"
                v-bind:x_mat="x_mat"
                v-bind:y_mat="y_mat"
              ></ResultWindow>
            </div>
            <el-slider
              v-model="result_index"
              :max="this.result_len - 1"
              show-input
            >
            </el-slider>

            <!-- <div>
              <DicomWindow
                v-bind:label="labels[1]"
                v-bind:mat="x_mat"
                v-bind:width="wnd_w"
                v-bind:height="wnd_h"
                v-bind:mat_width="mat_wids[1]"
                v-bind:mat_height="mat_heis[1]"
                v-bind:mat_row_spacing="pix_row_spacings[1]"
                v-bind:mat_col_spacing="pix_col_spacings[1]"
              ></DicomWindow>
            </div> -->
          </div>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span="12">
          <h3 style="margin: 0; line-height: 30px">窗口1</h3>
          <div v-bind:style="getStyle2()">
            <div>
              <VisibleWindow
                v-bind:label="labels[1]"
                v-bind:p_mat="mats1"
                v-bind:width="wnd_w"
                v-bind:height="wnd_h"
                v-bind:mat_row_spacing="pix_row_spacings[1]"
                v-bind:mat_col_spacing="pix_col_spacings[1]"
              ></VisibleWindow>
            </div>
            <el-slider v-model="x_index" :max="this.lens[1] - 1" show-input>
            </el-slider>
          </div>
        </el-col>

        <el-col :span="12">
          <h3 style="margin: 0; line-height: 30px">窗口2</h3>
          <div v-bind:style="getStyle2()">
            <!-- <input type="file" id="dicom_flies2" multiple="multiplt" placeholder="本地dicom文件上传"/> -->

            <!-- <input type="file" id="selectFile" multiple="multiplt" /> -->
            <div>
              <VisibleWindow
                v-bind:label="labels[2]"
                v-bind:p_mat="mats2"
                v-bind:width="wnd_w"
                v-bind:height="wnd_h"
                v-bind:mat_row_spacing="pix_row_spacings[2]"
                v-bind:mat_col_spacing="pix_col_spacings[2]"
              ></VisibleWindow>
            </div>
            <el-slider v-model="y_index" :max="this.lens[2] - 1" show-input>
            </el-slider>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import VisibleWindow from "./window/VisibleWindow";
import ResultWindow from "./window/ResultWindow";

// import * as math from "mathjs";
// import * as tf from "@tensorflow/tfjs";
// import sizeof from "object-sizeof";

// // //引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
// import * as cornerstone from "cornerstone-core";
// import * as dicomParser from "dicom-parser";

// // 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
// import * as cornerstoneWADOImageLoader from "../../../static/dist/cornerstoneWADOImageLoader.js";
// // var c = require("../../../static/opencvjs/opencv_js.js");
// import cv from "../../../static/opencvjs/opencv_js.js";

// // Cornerstone 工具外部依赖
// import Hammer from "hammerjs";
// import * as cornerstoneMath from "cornerstone-math";
// import * as cornerstoneTools from "cornerstone-tools";
// import { dot } from "mathlab";
// import { Tensor } from "@tensorflow/tfjs";
// // import DicomResultWindow from './dicomhandle/DicomResultWindow.vue';

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
// if (!cornerstoneWADOImageLoader.webWorkerManager.config) {
//   // console.log(cornerstoneWADOImageLoader.webWorkerManager.config);
//   cornerstoneWADOImageLoader.webWorkerManager.initialize(config);
// }

export default {
  name: "Controller",
  components: { VisibleWindow, ResultWindow },
  props: [
    "raws",
    "raw_change",
    "vers",
    "normals",
    "marks",
    "loading_vers_normals",
  ],
  data() {
    return {
      //窗口参数的设置
      // wnd_w: "256px",
      // wnd_h: "256px",
      active_state: {
        dcm0: Boolean,
        dcm1: Boolean,
        dcm2: Boolean,
      },

      wnd_w: 320,
      wnd_h: 320,

      //dicom文件的数据
      // dicoms0: "", //存储所有dicom文件
      // dicoms0_num: Number,
      // dicoms1_num: Number,
      slice_nums: Array,
      // dicoms0:"",

      x_pix_spacing: 1, //dicom文件width像素间距，1只是假定
      y_pix_spacing: 1,
      z_pix_spacing: 3,

      pix_row_spacings: Array,
      pix_col_spacings: Array,

      lens: Array,
      result_len: Number,

      // mat_wids: Array,
      // mat_heis: Array,
      // result_mat_width: Array,
      // result_mat_height: Array,

      //raws[i][j][k]中 x对应i，y对应j，z对应k
      x_mat: "",
      y_mat: "",
      z_mat: "",
      // x_total_len:Number,
      // y_total_len:Number,

      // z_total_len:Number,

      label_mat: Array,
      // mats: Array,
      mats0: Array,
      mats1: Array,
      mats2: Array,
      result_mats: "",

      z_index: Number, //当前的dicom文件座标
      x_index: Number,
      y_index: Number,
      result_index: Number,

      // raws[0]: "", //三维数据场
      read_num: Number, //表示当前异步读取文件数
      read_nums: Array,

      finished0: Boolean, //判断图像是否加载完成
      finished1: Boolean, //判断图像是否加载完成
      finished2: Boolean, //判断图像是否加载完成

      labels: Array,

      state: Number, //-1表示无影像，0表示单张影像，1表示影像融合，2表示体渲染

      slices: Array,
      // finishes: Array,

      magnifying: Boolean,
    };
  },
  created() {
    // this.x_len = 0;
    // this.y_len = 0;
    this.slices = new Array([0, 0, 0]);

    this.state = -1;
    this.read_nums = new Array([0, 0, 0]);
    this.mat_wids = new Array([0, 0, 0]);
    this.mat_heis = new Array([0, 0, 0]);
    this.imgs = new Array(3);
    this.result_mats = new Array(3);
    // this.pix_row_spacings = new Array([this.x_pix_spacing,this.y_pix_spacing,this.x_pix_spacing]);
    this.pix_row_spacings = new Array(3);

    this.pix_row_spacings[0] = this.x_pix_spacing;
    this.pix_row_spacings[1] = this.y_pix_spacing;
    this.pix_row_spacings[2] = this.x_pix_spacing;

    this.pix_col_spacings = new Array(3);
    this.pix_col_spacings[0] = this.y_pix_spacing;
    this.pix_col_spacings[1] = this.z_pix_spacing;
    this.pix_col_spacings[2] = this.z_pix_spacing;

    this.labels = new Array(3);
    this.labels[0] = "z";
    this.labels[1] = "x";
    this.labels[2] = "y";

    this.lens = new Array([1, 1, 1]);

    // this.finishes = new Array(false,false,false);

    this.active_state.dcm0 = false;
    this.active_state.dcm1 = false;
    this.active_state.dcm2 = false;

    this.x_len = 1;
    this.y_len = 1;
    this.z_len = 1;

    this.finished0 = false;
    this.finished1 = false;
    this.finished2 = false;

    this.read_num = 0;
    this.z_index = 0;
    this.slice_nums = new Array([0, 0, 0]);
    // this.dicoms0_num = 1;
  },
  mounted() {},
  methods: {
    // handleFileSelect(evt) {
    //   // console.log(111);

    //   evt.stopPropagation();
    //   evt.preventDefault();
    //   this.dicoms0 = evt.target.files;
    //   this.dicom= evt.target.files[0];
    //   this.imgs[0] = new Array(this.dicoms0.length);
    //   // this.imgs[0] = new Uint8Array(this.dicoms0.length);
    //   // console.log("imgs[0]",this.imgs[0]);
    //   this.dicoms_nums[0] = this.dicoms0.length;
    //   this.z_len = this.dicoms_nums[0];
    //   console.log(this.dicoms_nums[0]);

    //   // this.dicom = dicom;

    //   for (let i = 0; i < this.dicoms_nums[0]; i++) {
    //     // const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(this.dicoms0[i]);
    //     this.appendImg(this.dicoms0[i], i);
    //   }

    //   // const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(dicom);
    //   // this.getImg(imageId);
    // },

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
    appendImg(dcm, z_idx, idx) {
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(dcm);
      const _this = this;
      // console.log(this.read_num);
      cornerstone.loadAndCacheImage(imageId).then(
        function (image) {
          // if (_this.x_len < 0) {
          //   _this.x_len = image.width;
          //   _this.y_len = image.height;
          //   console.log(_this.x_len);
          // }
          // _this.x_len = image.width;
          // _this.y_len = image.height;
          // console.log(_this.x_len);

          // console.log(z_idx);

          // console.log("total_num",_this.dicoms_nums[idx])

          _this.imgs[idx][z_idx] = image;
          _this.read_nums[idx]++;
          if (_this.read_nums[idx] == _this.dicoms_nums[idx]) {
            if (idx == 0) {
              // console.log(1);
              _this.finished0 = true;
            } else if (idx == 1) {
              _this.finished1 = true;
            } else if (idx == 2) {
              _this.finished2 = true;
            }
            // _this.finished0 = true;
            console.log("加载完成", idx);
          }
          // console.log(_this.imgs[0]);
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
        "width: {0}px;height: {1}px;position: relative;color: white;display: inline-block;border-style: solid;border-color: black;",
        this.wnd_w + 0,
        this.wnd_h + 20
      );

      // console.log(style);
      return style;
    },
    getStyle2() {
      let style = this.StringFormat(
        "width: {0}px;height: {1}px;position: relative;color: white;margin:0 auto;",
        this.wnd_w + 0,
        this.wnd_h + 20
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

    array2mat(arr, row, col) {
      let len = arr.length;

      if (len != row * col) {
        throw new Error(
          this.StringFormat(
            "数组与矩阵必须匹配，当前数组长度{0}，而要求的矩阵宽度{1}，矩阵长度{2}",
            len,
            row,
            col
          )
        );
      }

      let mat = new Array(row);
      for (var i = 0; i < row; i++) {
        mat[i] = new Uint16Array(col);
      }

      for (let i = 0; i < row; i++) {
        for (let j = 0; j < col; j++) {
          mat[i][j] = arr[i * row + j];
        }
      }
      return mat;
    },

    process_dcms(dcms, idx) {
      this.imgs[idx] = new Array(dcms.length);

      this.dicoms_nums[idx] = dcms.length;
      // this.z_len = this.dicoms_nums[idx];
      this.read_nums[idx] = 0;
      // if(idx==1)console.log("before",this.read_num);
      // console.log(idx,this.dicoms_nums[idx]);
      for (let i = 0; i < this.dicoms_nums[idx]; i++) {
        this.appendImg(dcms[i], i, idx);
      }
    },
    getSliceX(idx, raw) {
      //获得X方向切片
      let y_len = raw[0].length;
      let z_len = raw[0][0].length;
      let mat = new Array(y_len);
      for (let i = 0; i < y_len; i++) {
        mat[i] = new Uint16Array(z_len);
      }

      for (let j = 0; j < y_len; j++) {
        for (let k = 0; k < z_len; k++) {
          mat[j][k] = raw[idx][j][k];
          // if(mat[j][k]!=0)no_zero+=1;
        }
      }
      return mat;
    },

    getSliceY(idx, raw) {
      let x_len = raw.length;
      let z_len = raw[0][0].length;
      let mat = new Array(x_len);
      for (let i = 0; i < x_len; i++) {
        mat[i] = new Uint16Array(z_len);
      }

      for (let i = 0; i < x_len; i++) {
        for (let k = 0; k < z_len; k++) {
          mat[i][k] = raw[i][idx][k];
          // if(mat[j][k]!=0)no_zero+=1;
        }
      }
      return mat;
    },

    getSliceZ(idx, raw) {
      let x_len = raw.length;
      let y_len = raw[0].length;
      let mat = new Array(x_len);
      for (let i = 0; i < x_len; i++) {
        mat[i] = new Uint16Array(y_len);
      }
      for (let i = 0; i < x_len; i++) {
        for (let j = 0; j < y_len; j++) {
          mat[i][j] = raw[i][j][idx];
          // if(mat[j][k]!=0)no_zero+=1;
        }
      }
      return mat;
    },

    min(arr) {
      let min = 10000;
      for (let i = 0; i < arr.length; i++) {
        if (arr[i] > 1 && arr[i] < min) min = arr[i];
      }
      return min;
    },

    overlay() {
      if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 >
        1
      ) {
        if (this.active_state.dcm0) {
          this.result_mats[0] = this.mats0;
        }

        if (this.active_state.dcm1) {
          // console.log("recive mat1");
          this.result_mats[1] = this.mats1;
        }

        if (this.active_state.dcm2) {
          this.result_mats[2] = this.mats2;
        }
      }
    },

    label() {
      if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 ==
        1
      ) {
        this.pix_row_spacings[0] = this.x_pix_spacing;
        this.pix_col_spacings[0] = this.y_pix_spacing;
        if (this.active_state.dcm0) {
          this.label_mat = this.mats0;
          this.result_len = this.raws[0][0][0].length;
        }
        if (this.active_state.dcm1) {
          // console.log("recive mat1");
          this.label_mat = this.mats1;
          this.result_len = this.raws[1][0][0].length;
        }
        if (this.active_state.dcm2) {
          this.label_mat = this.mats2;
          this.result_len = this.raws[2][0][0].length;
        }
      }
    },
    raws_num_test(r) {
      let count = 0;
      for (let i = 0; i < r.length; i++) {
        if (r[i] != undefined) {
          count += 1;
        }
      }
      return count;
    },
    resize_m(mat, x_alp, y_alp) {
      let x_len = mat.length;
      let y_len = mat[0].length;
      // console.log(x_len,y_len)

      let resize_x_len = Math.round(x_len * x_alp);
      let resize_y_len = Math.round(y_len * y_alp);

      let resize_mat = new Array(resize_x_len);
      for (let i = 0; i < resize_x_len; i++) {
        resize_mat[i] = new Array(resize_y_len);
        for (let j = 0; j < resize_y_len; j++) {
          let x = i / x_alp;
          let y = j / y_alp;
          let x0 = Math.floor(x);
          let y0 = Math.floor(y);
          let x1 = Math.ceil(x);
          let y1 = Math.ceil(y);
          let det = (y1 - y0) * (x1 - x0);

          if (x0 == x1 || y0 == y1) resize_mat[i][j] = mat[x0][y0];
          else {
            resize_mat[i][j] =
              0.25 * mat[x0][y0] +
              0.25 * mat[x1][y0] +
              0.25 * mat[x0][y1] +
              0.25 * mat[x1][y1];
          }
          // resize_raw[i][j][k] =
          //   (((y1 - y) * (x1 - x)) / det) * raw[x0][y0][k] +
          //   (((y1 - y) * (x - x0)) / det) * raw[x1][y0][k] +
          //   (((y - y0) * (x1 - x)) / det) * raw[x0][y1][k] +
          //   (((y - y0) * (x - x0)) / det) * raw[x1][y1][k];
        }
      }
      return resize_mat;
    },
  },
  computed: {
    // visible_states(){
    //   return this.$store.getters.visible_states;
    // }
  },
  watch: {
    z_index(new_z, old_z) {
      if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 ==
        1
      ) {
        //当前只有一张影像
        if (this.active_state.dcm0 == true) {
          this.mats0 = this.getSliceZ(new_z, this.raws[0]);
          // this.z_mat = this.mats0;
          if (this.$store.getters.visible_states[0] == "true") {
            this.z_mat = this.resize_m(
              this.mats0,
              this.x_pix_spacing,
              this.y_pix_spacing
            );
          } else {
            this.z_mat = [
              [0, 0],
              [0, 0],
            ];
          }
          // this.z_mat = this.resize_m(
          //   this.mats0,
          //   this.x_pix_spacing,
          //   this.y_pix_spacing
          // );
        }
      } else if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 >
        1
      ) {
        if (this.active_state.dcm0 == true) {
          this.mats0 = this.getSliceZ(new_z, this.raws[0]);
        }
      }
    },
    x_index(new_x, old_x) {
      if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 ==
        1
      ) {
        //当前只有一张影像
        if (this.active_state.dcm0 == true) {
          //0号影像加载
          this.mats1 = this.getSliceX(new_x, this.raws[0]);
          // this.x_mat = this.mats1;
          if (this.$store.getters.visible_states[1] == "true") {
            this.x_mat = this.resize_m(
              this.mats1,
              this.y_pix_spacing,
              this.z_pix_spacing
            );
          } else {
            this.x_mat = [
              [0, 0],
              [0, 0],
            ];
          }
        }
        if (this.active_state.dcm1 == true) {
          //1号影像加载
          this.mats1 = this.getSliceZ(new_x, this.raws[1]);
        }
      } else if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 >
        1
      ) {
        if (this.active_state.dcm1 == true) {
          //1号影像加载
          this.mats1 = this.getSliceZ(new_x, this.raws[1]);
        }
      }
    },
    y_index(new_y, old_y) {
      if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 ==
        1
      ) {
        //当前只有一张影像
        if (this.active_state.dcm0 == true) {
          //0号影像加载
          this.mats2 = this.getSliceY(new_y, this.raws[0]);
          // this.y_mat = this.mats2;
          if (this.$store.getters.visible_states[2] == "true") {
            this.y_mat = this.resize_m(
              this.mats2,
              this.x_pix_spacing,
              this.z_pix_spacing
            );
          } else {
            this.y_mat = [
              [0, 0],
              [0, 0],
            ];
          }
        }
        if (this.active_state.dcm2 == true) {
          //2号影像加载
          this.mats2 = this.getSliceZ(new_y, this.raws[1]);
        }
      } else if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 >
        1
      ) {
        if (this.active_state.dcm2 == true) {
          //2号影像加载
          this.mats2 = this.getSliceZ(new_y, this.raws[1]);
        }
      }
    },

    result_index(new_idx, old_idx) {
      if (
        this.active_state.dcm0 +
          this.active_state.dcm1 +
          this.active_state.dcm2 >
        1
      ) {
        if (this.active_state.dcm0) {
          let wnd_id = 0;
          this.result_mats[wnd_id] = this.getSliceZ(new_idx, this.raws[wnd_id]);
        }
        if (this.active_state.dcm1) {
          let wnd_id = 1;
          this.result_mats[wnd_id] = this.getSliceZ(new_idx, this.raws[wnd_id]);
        }
        if (this.active_state.dcm2) {
          let wnd_id = 2;
          this.result_mats[wnd_id] = this.getSliceZ(new_idx, this.raws[wnd_id]);
        }
      }
    },

    raw_change(n) {
      if (this.raws != undefined) {
        if (this.raws_num_test(this.raws) == 1) {
          for (let wnd_id = 0; wnd_id < this.raws.length; wnd_id++) {
            if (this.raws[wnd_id] != undefined) {
              this.labels[wnd_id] = "z";
              this.lens[wnd_id] = this.raws[wnd_id][0][0].length;
              this.pix_row_spacings[wnd_id] = this.x_pix_spacing;
              this.pix_col_spacings[wnd_id] = this.y_pix_spacing;

              switch (wnd_id) {
                case 0:
                  this.active_state.dcm0 = true;
                  this.labels[1] = "x";
                  this.labels[2] = "y";

                  this.lens[1] = this.raws[wnd_id].length;
                  this.lens[2] = this.raws[wnd_id][0].length;
                  this.z_index = Math.round(this.lens[0] / 2);
                  this.x_index = Math.round(this.lens[1] / 2);
                  this.y_index = Math.round(this.lens[2] / 2);

                  this.mats0 = this.getSliceZ(this.z_index, this.raws[wnd_id]);

                  this.mats1 = this.getSliceX(this.x_index, this.raws[wnd_id]);
                  this.mats2 = this.getSliceY(this.y_index, this.raws[wnd_id]);

                  this.pix_row_spacings[1] = this.y_pix_spacing;
                  this.pix_row_spacings[2] = this.x_pix_spacing;
                  this.pix_col_spacings[1] = this.z_pix_spacing;
                  this.pix_col_spacings[2] = this.z_pix_spacing;

                  break;
                case 1:
                  this.active_state.dcm1 = true;
                  this.x_index = Math.round(this.lens[1] / 2);
                  this.mats1 = this.getSliceZ(this.x_index, this.raws[wnd_id]);

                  break;
                case 2:
                  this.active_state.dcm2 = true;
                  this.y_index = Math.round(this.lens[2] / 2);
                  this.mats2 = this.getSliceZ(this.y_index, this.raws[wnd_id]);
                  break;
                default:
                  break;
              }
            }
          }
          if (this.$store.getters.result_view_state == 2) {
            this.label();
          }
        } else if (this.raws_num_test(this.raws) > 1) {
          for (let wnd_id = 0; wnd_id < this.raws.length; wnd_id++) {
            if (this.raws[wnd_id] != undefined) {
              this.labels[wnd_id] = "z";
              this.lens[wnd_id] = this.raws[wnd_id][0][0].length;
              this.slice_nums[wnd_id] = this.raws[wnd_id][0][0].length;
              this.pix_row_spacings[wnd_id] = this.x_pix_spacing;
              this.pix_col_spacings[wnd_id] = this.y_pix_spacing;
              switch (wnd_id) {
                case 0:
                  this.active_state.dcm0 = true;
                  this.z_index = Math.round(this.lens[0] / 2);
                  this.mats0 = this.getSliceZ(this.z_index, this.raws[wnd_id]);
                  break;
                case 1:
                  this.active_state.dcm1 = true;
                  this.x_index = Math.round(this.lens[1] / 2);

                  this.mats1 = this.getSliceZ(1, this.raws[wnd_id]);
                  break;
                case 2:
                  this.y_index = Math.round(this.lens[2] / 2);

                  this.active_state.dcm2 = true;
                  this.mats2 = this.getSliceZ(y_index, this.raws[wnd_id]);
                  break;
                default:
                  break;
              }
            }
          }
          this.result_len = this.min(this.slice_nums);
          this.overlay();
        }
      }
    },
    "$store.state.visible.result_view_state"(new_state) {
      if (new_state == 2) {
        this.label();
      }
    },
    "$store.state.visible.visible_states"(new_states) {
      if (new_states[0] == "true") {
        this.z_mat = this.resize_m(
          this.mats0,
          this.x_pix_spacing,
          this.y_pix_spacing
        );
      } else {
        this.z_mat = [
          [0, 0],
          [0, 0],
        ];
      }

      if (new_states[1] == "true") {
        this.x_mat = this.resize_m(
          this.mats1,
          this.y_pix_spacing,
          this.z_pix_spacing
        );
      } else {
        this.x_mat = [
          [0, 0],
          [0, 0],
        ];
      }

      if (new_states[2] == "true") {
        this.y_mat = this.resize_m(
          this.mats2,
          this.x_pix_spacing,
          this.z_pix_spacing
        );
      } else {
        this.y_mat = [
          [0, 0],
          [0, 0],
        ];
      }
    },
  },
};
</script>

<style>
.el-row {
  margin-bottom: 20px;
  /* &:last-child {
      margin-bottom: 0;
    } */
}
.el-col {
  border-radius: 4px;
}
.bg-purple-dark {
  background: #99a9bf;
}
.bg-purple {
  background: #d3dce6;
}
.bg-purple-light {
  background: #e5e9f2;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
}
.row-bg {
  padding: 10px 0;
  background-color: #f9fafc;
}
</style>