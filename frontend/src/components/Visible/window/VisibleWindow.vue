<template>
  <div>
    <!-- <div
      id="dicomImage"
      v-bind:style="getStyle()"
    ></div> -->
    <div ref="dicomImage">
    </div>
    <!-- <input id="test" type ="button" style="position: absolute;"/> -->
  </div>
</template>

<script>
// import * as tf from "@tensorflow/tfjs";
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
  name: "VisibleWindow",
  props: [
    "mat",
    "width",
    "height",
    "mat_row_spacing",
    "mat_col_spacing",
    "label",
    "matting_on",
    "matting_state",
  ],
  //其中mat是dicomController传过来的切片矩阵，
  //width,heigth是针对dom元素的长宽
  //mat_width，mat_height是mat的宽度高度
  //mat_row_spacing,mat_col_spacing是原dicom文件中像素距离，可以看作渲染时的缩放倍数
  data() {
    return {
      container: "",
      alpha: Number,
      beta: Number,
      view: {
        scene: "",
        renderer: "",
        camera: "",
        geometry: "",
        mesh: "",
      }, //与渲染相关的变量都在这里
      init_finish: Boolean,
      rect: "", //(x0,y0,x1,y1)的形式
      mat_width:Number,
      mat_height:Number,

      // file: "",
      // img:"",
      // test_data:"",
    };
  },
  created() {
    // this.matting_on = false;
    // if (this.matting_state == undefined) this.matting_state = 0;
    this.mat_width = 0;
    this.mat_height = 0;
    this.beta = 1.0;
    this.alpha = 256;
    this.init_finish = false;
    this.rect = { x0: Number, y0: Number, x1: Number, y1: Number };
  },
  mounted() {
    this.initRender();
  },
  methods: {
    initRender() {
      this.view.scene = new THREE.Scene();
      this.view.camera = new THREE.PerspectiveCamera(
        75,
        this.width / this.height,
        0.1,
        1500
      );
      this.view.renderer = new THREE.WebGLRenderer();
      this.view.renderer.setSize(this.width, this.height);

      this.container = this.$refs.dicomImage;
      // const container = document.getElementById("dicomImage");
      this.container.appendChild(this.view.renderer.domElement);
      this.container.addEventListener("mousewheel", this.mousewheel, false);
      this.container.addEventListener("mousedown", this.mousedown, false);
      // this.container.addEventListener("click", this.click, false);
      // this.rect = this.view.renderer.domElement.getBoundingClientRect().x;

      this.rect.x0 = Number(
        this.view.renderer.domElement.getBoundingClientRect().x
      );
      this.rect.y0 = Number(
        this.view.renderer.domElement.getBoundingClientRect().y
      );
      this.rect.x1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().right
      );
      this.rect.y1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().bottom
      );

      this.view.camera.position.z = 500;
      // this.view.camera.up.x = - 1;
      // this.view.camera.up.y = 0;
      this.view.camera.lookAt(new THREE.Vector3(0, 0, 0));

      this.view.geometry = new THREE.BufferGeometry();
      // this.view.geometry.center();
      let material = new THREE.MeshBasicMaterial({
        vertexColors: THREE.VertexColors,
      }); //这里渲染方式应该是简单插值，但效果感觉不是很好
      this.view.mesh = new THREE.Mesh(this.view.geometry, material);

      // this.view.mesh.scale.set(this.mat_row_spacing, this.mat_col_spacing);
      // if (this.label == "z") this.view.mesh.rotateZ(-Math.PI / 2);
      // console.log(this.view.geometry);

      if (this.label == "z") this.view.mesh.rotateZ(-Math.PI / 2);
      // else if (this.label == "x") this.view.mesh.rotateZ(-Math.PI);

      this.view.scene.add(this.view.mesh);

      this.render();
      this.init_finish = true;
    },
    render() {
      requestAnimationFrame(this.render);
      this.view.renderer.render(this.view.scene, this.view.camera);
    },
    reset_beta(beta) {//设置亮度
      // let k = 0;
      let ncolors = this.view.geometry.getAttribute("color").array;

      for (let i = 0; i < ncolors.length; i++) {
        ncolors[i] = ncolors[i] * beta;
      }
      // this.view.geometry = new THREE.BufferGeometry();
      this.view.geometry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
      // if (this.label == "z") this.view.mesh.rotateZ(-Math.PI / 2);
      // this.view.mesh.scale.set(this.mat_row_spacing, this.mat_col_spacing);

      // this.view.geometry.center();
    },
    get_m_mouse_pos(
      rect,
      m_wid,
      m_hei,
      m_center_x,
      m_center_y,
      mouse_x,
      mouse_y
    ) {
      let cx = (rect.x0 + rect.x1) / 2;
      let cy = (rect.y0 + rect.y1) / 2;
      let wid = rect.x1 - rect.x0;
      let hei = rect.y1 - rect.y0;
      // let disX = e.clientX;
      // let disY = e.clientY;
      let dx = mouse_x - cx;
      let dy = mouse_y - cy;

      dx = (m_wid / wid) * dx;
      dy = (-m_hei / hei) * dy;
      let m_mouse_pos = {
        x: m_center_x + dx,
        y: m_center_y + dy,
      };
      // console.log(rect);
      // console.log(m_mouse_pos);
      // console.log(mouse_pos);
      return m_mouse_pos;
    },
    m_t(w, h, x, y) {
      return (
        (h < x && w < this.mat_height - y) || (h > x && w > this.mat_height - y)
      );
    },
    reverse_mat(mat) {
      let wid = mat.length;
      let hei = mat[0].length;
      let r_mat = new Array(hei);
      for (let i = 0; i < hei; i++) {
        r_mat[i] = new Array(wid);
        for (let j = 0; j < wid; j++) {
          r_mat[i][j] = mat[j][i];
        }
      }
      return r_mat;
    },
    set_matting(x, y, mat, row, col, matting_state, alp, beta) {//设置fusion
      let k = 0;
      x = x + row / 2;
      y = y + col / 2;
      console.log(x, y);
      let ncolors = new Float32Array((row - 1) * (col - 1) * 6 * 3);
      if (matting_state == 0 || matting_state == undefined) {
        // console.log(1);
        for (let i = 0; i < row - 1; i++) {
          for (let j = 0; j < col - 1; j++) {
            //每一个循环针对一个正方形方格，每一个正方形方格中有两个三角形面片，这个顺序很重要，不能改（我也不知道原理）
            // let p0 = [i,j,0];
            // let p1 = [i,j+1,0];
            // let p2 = [i+1,j,0];
            // let p3 = [i+1,j+1,0];

            //第一个三角形
            //第一个点
            // if(i == 10){
            //   console.log((i < x && j < y) || (i > x && j > y));

            // }

            if (this.m_t(i, j, x, y)) {
              ncolors[k] = (mat[i][j] / alp) * beta;
              ncolors[k + 1] = (mat[i][j] / alp) * beta;
              ncolors[k + 2] = (mat[i][j] / alp) * beta;
            } else {
              ncolors[k] = 0;
              ncolors[k + 1] = 0;
              ncolors[k + 2] = 0;
            }

            //第二个点
            if (this.m_t(i + 1, j, x, y)) {
              ncolors[k + 3] = (mat[i + 1][j] / alp) * beta;
              ncolors[k + 4] = (mat[i + 1][j] / alp) * beta;
              ncolors[k + 5] = (mat[i + 1][j] / alp) * beta;
            } else {
              ncolors[k + 3] = 0;
              ncolors[k + 4] = 0;
              ncolors[k + 5] = 0;
            }

            if (this.m_t(i, j + 1, x, y)) {
              ncolors[k + 6] = (mat[i][j + 1] / alp) * beta;
              ncolors[k + 7] = (mat[i][j + 1] / alp) * beta;
              ncolors[k + 8] = (mat[i][j + 1] / alp) * beta;
            } else {
              ncolors[k + 6] = 0;
              ncolors[k + 7] = 0;
              ncolors[k + 8] = 0;
            }

            //第三个点

            //第二个三角形
            //第一个点

            if (this.m_t(i + 1, j + 1, x, y)) {
              ncolors[k + 9] = (mat[i + 1][j + 1] / alp) * beta;
              ncolors[k + 10] = (mat[i + 1][j + 1] / alp) * beta;
              ncolors[k + 11] = (mat[i + 1][j + 1] / alp) * beta;
            } else {
              ncolors[k + 9] = 0;
              ncolors[k + 10] = 0;
              ncolors[k + 11] = 0;
            }

            //第二个点
            if (this.m_t(i, j + 1, x, y)) {
              ncolors[k + 12] = (mat[i][j + 1] / alp) * beta;
              ncolors[k + 13] = (mat[i][j + 1] / alp) * beta;
              ncolors[k + 14] = (mat[i][j + 1] / alp) * beta;
            } else {
              ncolors[k + 12] = 0;
              ncolors[k + 13] = 0;
              ncolors[k + 14] = 0;
            }

            if (this.m_t(i + 1, j, x, y)) {
              ncolors[k + 15] = (mat[i + 1][j] / alp) * beta;
              ncolors[k + 16] = (mat[i + 1][j] / alp) * beta;
              ncolors[k + 17] = (mat[i + 1][j] / alp) * beta;
            } else {
              ncolors[k + 15] = 0;
              ncolors[k + 16] = 0;
              ncolors[k + 17] = 0;
            }
            // if(i - x < 5 && j - y < 5){
            //   // console.log(1);
            //   for (let l = 0; l < 3; l++) {
            //     ncolors[k + l] = 1;

            //   }
            // }

            // if(mat[i][j] >= 255 && this.label =="z" )abnorm+=1;

            // for (let ind = 0; ind < 18; ind++) {
            //   ncolors[k+ind]=0.5;

            // }
            k += 18;
          }
        }
      }

      this.view.geometry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
    },

    click(e) {
      e.preventDefault();
      e.stopPropagation();

      if (this.matting_on == 1) {
        // console.log(1111);

        let mouse_pos = this.get_m_mouse_pos(
          this.rect,
          this.mat_width,
          this.mat_height,
          this.view.camera.position.x,
          this.view.camera.position.y,
          e.clientX,
          e.clientY
        );
        this.set_matting(
          mouse_pos.x,
          mouse_pos.y,
          this.mat,
          this.mat_width,
          this.mat_height,
          this.matting_state,
          this.alpha,
          this.beta
        );
        // console.log(mouse_pos);
      }
    },

    mousewheel(e) {
      e.preventDefault();
      //e.stopPropagation();
      if (e.wheelDelta) {
        //判断浏览器IE，谷歌滑轮事件
        if (e.wheelDelta > 0) {
          //当滑轮向上滚动时
          if (this.view.camera.position.z > 0)
            this.view.camera.position.z -= 50;
          // fov -= near < fov ? 1 : 0;
        }
        if (e.wheelDelta < 0) {
          //当滑轮向下滚动时
          this.view.camera.position.z += 50;
          // fov += fov < far ? 1 : 0;
        }
      } else if (e.detail) {
        //Firefox滑轮事件
        if (e.detail > 0) {
          //当滑轮向上滚动时
          if (this.view.camera.position.z > 0)
            this.view.camera.position.z -= 50;
          // fov -= 1;
        }
        if (e.detail < 0) {
          //当滑轮向下滚动时
          this.view.camera.position.z += 50;
          // fov += 1;
        }
      }
      // this.view.camera.fov = fov;
      this.view.camera.updateProjectionMatrix();
      this.view.renderer.render(this.view.scene, this.view.camera);
      //updateinfo();
    },

    mousedown(e) {
      const _this = this;
      // console.log(this.label,"鼠标已按下");
      let disX = e.clientX;
      let disY = e.clientY;
      let o_poistion_x = this.view.camera.position.x;
      let o_poistion_y = this.view.camera.position.y;
      if (e.button == 0) {
        this.container.onmousemove = function (e) {
          //计算需要移动的距离
          let dx = e.clientX - disX;
          let dy = e.clientY - disY;
          _this.view.camera.position.x = o_poistion_x + dx;
          _this.view.camera.position.y = o_poistion_y + dy;
        };
      }

      this.container.onmouseup = function (e) {
        if (e.button == 2) {
          let dx = e.clientX - disX;
          let beta = 1 + dx / 1000;
          _this.beta = _this.beta * beta;
          if (beta <= 0.001) beta = 0.001;
          // _this.reset_beta(_this.beta);
          _this.reset_beta(
            beta
          );
        }
        _this.container.onmousemove = null;
        _this.container.onmouseup = null;
      };
      // console.log(this.container.onmousemove);
    },
    // mousemove(e, disX, disY,o_poistion_x,o_poistion_y) {
    //   let dx = e.clientX - disX;
    //   let dy = e.clientY - disY;
    //   // console.log(dx,dy);
    //   this.view.camera.position.x = o_poistion_x + dx;
    //   this.view.camera.position.y = o_poistion_y + dy;
    // },

    imgAdd(mat, row, col, alp) {//添加医学影像
      // //以三角形面片为单位！！！！
      // let row = this.mat_width;
      // let col = this.mat_height;
      // console.log(row,col)

      let k = 0;
      let vertices = new Float32Array((row - 1) * (col - 1) * 6 * 3);
      let ncolors = new Float32Array((row - 1) * (col - 1) * 6 * 3);

      // let abnorm = 0;
      for (let i = 0; i < row - 1; i++) {
        for (let j = 0; j < col - 1; j++) {
          //每一个循环针对一个正方形方格，每一个正方形方格中有两个三角形面片，这个顺序很重要，不能改（我也不知道原理）
          // let p0 = [i,j,0];
          // let p1 = [i,j+1,0];
          // let p2 = [i+1,j,0];
          // let p3 = [i+1,j+1,0];

          //第一个三角形
          //第一个点
          vertices[k] = i;
          vertices[k + 1] = j;
          vertices[k + 2] = 0;
          ncolors[k] = mat[i][j] / alp;
          ncolors[k + 1] = mat[i][j] / alp;
          ncolors[k + 2] = mat[i][j] / alp;

          //第二个点
          vertices[k + 3] = i + 1;
          vertices[k + 4] = j;
          vertices[k + 5] = 0;
          ncolors[k + 3] = mat[i + 1][j] / alp;
          ncolors[k + 4] = mat[i + 1][j] / alp;
          ncolors[k + 5] = mat[i + 1][j] / alp;

          //第三个点
          vertices[k + 6] = i;
          vertices[k + 7] = j + 1;
          vertices[k + 8] = 0;
          ncolors[k + 6] = mat[i][j + 1] / alp;
          ncolors[k + 7] = mat[i][j + 1] / alp;
          ncolors[k + 8] = mat[i][j + 1] / alp;

          //第二个三角形
          //第一个点
          vertices[k + 9] = i + 1;
          vertices[k + 10] = j + 1;
          vertices[k + 11] = 0;
          ncolors[k + 9] = mat[i + 1][j + 1] / alp;
          ncolors[k + 10] = mat[i + 1][j + 1] / alp;
          ncolors[k + 11] = mat[i + 1][j + 1] / alp;

          //第二个点
          vertices[k + 12] = i;
          vertices[k + 13] = j + 1;
          vertices[k + 14] = 0;
          ncolors[k + 12] = mat[i][j + 1] / alp;
          ncolors[k + 13] = mat[i][j + 1] / alp;
          ncolors[k + 14] = mat[i][j + 1] / alp;

          //第三个点
          vertices[k + 15] = i + 1;
          vertices[k + 16] = j;
          vertices[k + 17] = 0;
          ncolors[k + 15] = mat[i + 1][j] / alp;
          ncolors[k + 16] = mat[i + 1][j] / alp;
          ncolors[k + 17] = mat[i + 1][j] / alp;

          // if(mat[i][j] >= 255 && this.label =="z" )abnorm+=1;

          // for (let ind = 0; ind < 18; ind++) {
          //   ncolors[k+ind]=0.5;

          // }
          k += 18;
        }
      }
      // console.log(abnorm);

      // this.view.geometry = new THREE.BufferGeometry();
      this.view.geometry.setAttribute(
        "position",
        new THREE.BufferAttribute(vertices, 3)
      );
      this.view.geometry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
      // if (this.label == "z") this.view.mesh.rotateZ(-Math.PI / 2);
      this.view.mesh.scale.set(this.mat_row_spacing, this.mat_col_spacing);
      // if (this.label == "y") this.view.mesh.rotateX(-Math.PI );

      this.view.geometry.center();
      // if (this.label == "y") this.view.mesh.rotateX(-Math.PI);
      //       正方形渲染的顺序，一定不能乱
      // //       var vertices = new Float32Array( [
      // // 	 0.0,  0.0,  1.0,
      // // 	 1.0,  0.0,  1.0,
      // // 	 0.0,  1.0,  1.0,

      // // 	 1.0,  1.0,  1.0,
      // // 	 0.0,  1.0,  1.0,
      // // 	 1.0,  0.0,  1.0
      // // ] );

      // this.render();
    },
    // handleDragOver(evt) {
    //   evt.stopPropagation();
    //   evt.preventDefault();
    //   evt.dataTransfer.dropEffect = "copy"; // Explicitly show this is a copy.
    // },

    // showView(image) {
    //   if (image != undefined) {
    //     // console.log("image",image);
    //     var element = document.getElementById("dicomImage");
    //     var viewport = cornerstone.getDefaultViewportForImage(element, image);
    //     // viewport.displayedArea.brhc.x=256;
    //     // viewport.displayedArea.brhc.y=256;
    //     // viewport.scale=0.5;
    //     // console.log(viewport);

    //     cornerstone.displayImage(element, image, viewport);
    //   }
    // },
    matting_rm(mat, row, col, alp) {//删除fusion的效果
      let k = 0;
      let ncolors = new Float32Array((row - 1) * (col - 1) * 6 * 3);

      // let abnorm = 0;
      for (let i = 0; i < row - 1; i++) {
        for (let j = 0; j < col - 1; j++) {
          //每一个循环针对一个正方形方格，每一个正方形方格中有两个三角形面片，这个顺序很重要，不能改（我也不知道原理）
          // let p0 = [i,j,0];
          // let p1 = [i,j+1,0];
          // let p2 = [i+1,j,0];
          // let p3 = [i+1,j+1,0];

          //第一个三角形
          //第一个点
          ncolors[k] = mat[i][j] / alp;
          ncolors[k + 1] = mat[i][j] / alp;
          ncolors[k + 2] = mat[i][j] / alp;

          //第二个点
          ncolors[k + 3] = mat[i + 1][j] / alp;
          ncolors[k + 4] = mat[i + 1][j] / alp;
          ncolors[k + 5] = mat[i + 1][j] / alp;

          //第三个点
          ncolors[k + 6] = mat[i][j + 1] / alp;
          ncolors[k + 7] = mat[i][j + 1] / alp;
          ncolors[k + 8] = mat[i][j + 1] / alp;

          //第二个三角形
          //第一个点
          ncolors[k + 9] = mat[i + 1][j + 1] / alp;
          ncolors[k + 10] = mat[i + 1][j + 1] / alp;
          ncolors[k + 11] = mat[i + 1][j + 1] / alp;

          //第二个点
          ncolors[k + 12] = mat[i][j + 1] / alp;
          ncolors[k + 13] = mat[i][j + 1] / alp;
          ncolors[k + 14] = mat[i][j + 1] / alp;

          //第三个点
          ncolors[k + 15] = mat[i + 1][j] / alp;
          ncolors[k + 16] = mat[i + 1][j] / alp;
          ncolors[k + 17] = mat[i + 1][j] / alp;

          // if(mat[i][j] >= 255 && this.label =="z" )abnorm+=1;

          // for (let ind = 0; ind < 18; ind++) {
          //   ncolors[k+ind]=0.5;

          // }
          k += 18;
        }
      }
      // console.log(abnorm);

      this.view.geometry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
    },

    getStyle() {
      let style = this.StringFormat(
        "width: {0}px;height: {1}px;top: 0px;left: 0px;position: absolute;",
        this.width,
        this.height
      );

      // console.log(style);
      return style;
    },
  },

  watch: {
    mat(new_m, old_m) {
      if (new_m != undefined) {
        // console.log(new_m);
        this.mat_width = new_m.length;
        this.mat_height = new_m[0].length;
        this.imgAdd(new_m, this.mat_width, this.mat_height, this.alpha);
      }
    },
    label(new_label, old_label) {
      // if (new_label == "z" && old_label == "x" && this.init_finish) {
      //   this.view.mesh.rotateZ(Math.PI / 2);
      // } else if (new_label == "z" && old_label == "y" && this.init_finish) {
      //   this.view.mesh.rotateZ(Math.PI / 2);

      // }
      if(new_label='z' && old_label != 'z'){
        this.view.mesh.rotateZ(- Math.PI / 2);
      }

    },
    matting_on(new_l, old_l) {
      if (new_l == 1 && this.container != "" && this.label == "z") {
        this.container.addEventListener("click", this.click, false);
      } else if (
        new_l == 0 &&
        old_l == 1 &&
        this.container != "" &&
        this.label == ""
      ) {
        // this.container.addEventListener("click", this.click, false);
        // this.container.click = null;
        this.container.removeEventListener("click", this.click, false);
        this.matting_rm(this.mat, this.mat_width, this.mat_height, this.alpha);
      }
    },
  },
};
</script>