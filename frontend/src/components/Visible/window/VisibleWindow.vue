<template>
  <div>
    <!-- <div
      id="dicomImage"
      v-bind:style="getStyle()"
    ></div> -->
    <div ref="dicomImage"></div>
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
    "p_mat",
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

        scale_gemetry: "",
        scale_mesh: "",
      }, //与渲染相关的变量都在这里
      init_finish: Boolean,
      rect: "", //(x0,y0,x1,y1)的形式
      mat_width: Number,
      mat_height: Number,
      mat:Array,

      scale_glass: {
        s_wid: Number,
        s_hei: Number, //放大镜窗口大小（未放缩前，在原来矩阵的尺度上）
        zoom: Number,
        s_mat: Array,
      },

      // file: "",
      // img:"",
      // test_data:"",
    };
  },
  created() {
    // this.matting_on = false;
    // if (this.matting_state == undefined) this.matting_state = 0;

    this.scale_glass.s_wid = 50;
    this.scale_glass.s_hei = 50;
    this.scale_glass.zoom = 3;
    this.scale_w;
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

      // if (this.label == "z") this.view.mesh.rotateZ(-Math.PI / 2);
      // else if (this.label == "x") this.view.mesh.rotateZ(-Math.PI);

      this.view.scene.add(this.view.mesh);

      this.render();
      this.init_finish = true;
    },

    scale_init() {
      this.view.scale_gemetry = new THREE.BufferGeometry();
      let scale_material = new THREE.MeshBasicMaterial({
        vertexColors: THREE.VertexColors,
      });

      this.view.scale_mesh = new THREE.Mesh(
        this.view.scale_gemetry,
        scale_material
      );
      this.view.scene.add(this.view.scale_mesh);
    },
    render() {
      requestAnimationFrame(this.render);
      this.view.renderer.render(this.view.scene, this.view.camera);
    },
    reset_beta(beta) {
      //设置亮度
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

    remove_scale(){
      this.view.scene.remove(this.view.scale_mesh);
      this.view.scale_mesh.geometry.dispose();
      this.view.scale_mesh.material.dispose();
      this.view.scale_mesh = undefined;
      
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


    reverse_mat(mat) {
      let x = mat.length;
      let y = mat[0].length;

      let new_mat = new Array(y);
      for (let i = 0; i < y; i++) {
        new_mat[i] = new Array(x);
        for (let j = 0; j < x; j++) {
          new_mat[i][j] = mat[y - j - 1][x - i - 1];
        }
      }
      return new_mat;
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
        // this.set_matting(
        //   mouse_pos.x,
        //   mouse_pos.y,
        //   this.mat,
        //   this.mat_width,
        //   this.mat_height,
        //   this.matting_state,
        //   this.alpha,
        //   this.beta
        // );
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
          _this.reset_beta(beta);
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

    scale_operate(e) {
      e.preventDefault();
      const _this = this;

      if (e.button == 0) {
        let PI = 3.1415926;
        let fov = (this.view.camera.fov / 180) * PI;
        let aspect = this.view.camera.aspect;
        let d = this.view.camera.position.z;
        let wid = Math.tan(fov / 2) * d * 2;
        let hei = Math.tan(fov / 2) * d * 2 * aspect;
        let rect = this.get_rect();
        let mouse_pos = this.get_mouse_coord(
          rect,
          wid,
          hei,
          this.view.camera.position.x,
          this.view.camera.position.y,
          e.clientX,
          e.clientY
        );

        let child_mat = this.get_child_mat(
          this.mat,
          mouse_pos.x,
          mouse_pos.y,
          this.scale_glass.s_wid,
          this.scale_glass.s_hei
        );
        if(child_mat != null){
          this.scaleAdd(
          child_mat,
          mouse_pos.x,
          mouse_pos.y,
          this.alpha,
          this.scale_glass.zoom
        );
        }
        
      }
    },

    get_child_mat(mat, mid_x, mid_y, wid, hei) {
      let row = mat.length;
      let col = mat[0].length;

      mid_x = Math.round(mid_x + row / 2);
      mid_y = Math.round(mid_y + col / 2);

      let sx = Math.max(mid_x - wid / 2, 0);
      let ex = Math.min(mid_x + wid / 2, row - 1);

      let sy = Math.max(mid_y - hei / 2, 0);
      let ey = Math.min(mid_y + hei / 2, col - 1);

      if (ex > sx && ey > sy) {
        let child_m = new Array(ex - sx);

        for (let i = 0; i < ex - sx; i++) {
          child_m[i] = new Uint16Array(ey - sy);
          for (let j = 0; j < ey - sy; j++) {
            child_m[i][j] = mat[i + sx][j + sy];
          }
        }
        return child_m;
      }

      else return null;
    },

    get_rect() {
      let rect = { x0: "", y0: "", x1: "", y1: "" };
      rect.x0 = Number(this.view.renderer.domElement.getBoundingClientRect().x);
      rect.y0 = Number(this.view.renderer.domElement.getBoundingClientRect().y);
      rect.x1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().right
      );
      rect.y1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().bottom
      );
      return rect;
    },

    get_mouse_coord(//根据鼠标位置获取切面坐标
      rect,
      m_wid,
      m_hei,
      m_center_x,
      m_center_y,
      mouse_x,
      mouse_y
    ) {
      //rect代表当前窗口矩形框位置与长宽；m_wid代表中心窗口宽，m_hei代表窗口高
      //m_center_x,m_center_y代表当前相机x与y坐标
      //mouse_x,mouse_y代表浏览器中鼠标位置

      let cx = (rect.x0 + rect.x1) / 2;
      let cy = (rect.y0 + rect.y1) / 2;
      let wid = rect.x1 - rect.x0;
      let hei = rect.y1 - rect.y0;
      // let disX = e.clientX;
      // let disY = e.clientY;
      let dx = mouse_x - cx;
      let dy = mouse_y - cy;

      dx = (m_wid / wid) * dx;
      dy = -(m_hei / hei) * dy;
      let m_mouse_pos = {
        x: m_center_x + dx,
        y: m_center_y + dy,
      };

      return m_mouse_pos;
    },

    scaleAdd(mat, mid_x, mid_y, alp, zoom) {
      let row = mat.length;
      let col = mat[0].length;

      let wid2 = row / 2;
      let hei2 = col / 2;

      mid_x = Math.round(mid_x);
      mid_y = Math.round(mid_y);

      // console.log(mid_x - wid2, mid_y - hei2);

      let k = 0;
      let vertices = new Float32Array((row - 1) * (col - 1) * 6 * 3);
      let ncolors = new Float32Array((row - 1) * (col - 1) * 6 * 3);

      // let abnorm = 0;
      for (let i = 0; i < row - 1; i++) {
        for (let j = 0; j < col - 1; j++) {
          //第一个点
          vertices[k] = i - wid2;
          vertices[k + 1] = j - hei2;
          vertices[k + 2] = 1;
          ncolors[k] = mat[i][j] / alp;
          ncolors[k + 1] = mat[i][j] / alp;
          ncolors[k + 2] = mat[i][j] / alp;

          //第二个点
          vertices[k + 3] = i + 1 - wid2;
          vertices[k + 4] = j - hei2;
          vertices[k + 5] = 1;
          ncolors[k + 3] = mat[i + 1][j] / alp;
          ncolors[k + 4] = mat[i + 1][j] / alp;
          ncolors[k + 5] = mat[i + 1][j] / alp;

          //第三个点
          vertices[k + 6] = i - wid2;
          vertices[k + 7] = j + 1 - hei2;
          vertices[k + 8] = 1;
          ncolors[k + 6] = mat[i][j + 1] / alp;
          ncolors[k + 7] = mat[i][j + 1] / alp;
          ncolors[k + 8] = mat[i][j + 1] / alp;

          //第二个三角形
          //第一个点
          vertices[k + 9] = i + 1 - wid2;
          vertices[k + 10] = j + 1 - hei2;
          vertices[k + 11] = 1;
          ncolors[k + 9] = mat[i + 1][j + 1] / alp;
          ncolors[k + 10] = mat[i + 1][j + 1] / alp;
          ncolors[k + 11] = mat[i + 1][j + 1] / alp;

          //第二个点
          vertices[k + 12] = i - wid2;
          vertices[k + 13] = j + 1 - hei2;
          vertices[k + 14] = 1;
          ncolors[k + 12] = mat[i][j + 1] / alp;
          ncolors[k + 13] = mat[i][j + 1] / alp;
          ncolors[k + 14] = mat[i][j + 1] / alp;

          //第三个点
          vertices[k + 15] = i + 1 - wid2;
          vertices[k + 16] = j - hei2;
          vertices[k + 17] = 1;
          ncolors[k + 15] = mat[i + 1][j] / alp;
          ncolors[k + 16] = mat[i + 1][j] / alp;
          ncolors[k + 17] = mat[i + 1][j] / alp;

          k += 18;
        }
      }

      // console.log(vertices)

      this.view.scale_gemetry.setAttribute(
        "position",
        new THREE.BufferAttribute(vertices, 3)
      );

      // this.view.geometry.setAttribute(
      //   "position",
      //   new THREE.BufferAttribute(vertices, 3)
      // );
      this.view.scale_gemetry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
      this.view.scale_mesh.scale.set(
        this.mat_row_spacing * zoom,
        this.mat_col_spacing * zoom
      );
      this.view.scale_mesh.position.set(mid_x,mid_y)

      // this.view.scale_mesh.scale.set(zoom, zoom);
    },

    //将切面矩阵转化为可以被WebGL接收的顶点值与颜色值
    imgAdd(mat, alp) { 
      //mat代表切面矩阵，alp是一个修订值

      let row = mat.length;
      let col = mat[0].length;
      let wid2 = row / 2;
      let hei2 = col / 2;

      let k = 0;
      let vertices = new Float32Array((row - 1) * (col - 1) * 6 * 3);
      //顶点数组
      let ncolors = new Float32Array((row - 1) * (col - 1) * 6 * 3);
      //颜色数组

      // let abnorm = 0;
      for (let i = 0; i < row - 1; i++) {
        for (let j = 0; j < col - 1; j++) {
          //每一个循环针对一个正方形方格，
          //每一个正方形方格中有两个三角形面片，
          //这个顺序很重要，不能改

          // let p0 = [i,j,0];let p1 = [i,j+1,0]; 
          //let p2 = [i+1,j,0]; let p3 = [i+1,j+1,0];

          //第一个三角形
          //第一个点
          vertices[k] = i - wid2;
          vertices[k + 1] = j - hei2;
          vertices[k + 2] = 0;
          ncolors[k] = mat[i][j] / alp;
          ncolors[k + 1] = mat[i][j] / alp;
          ncolors[k + 2] = mat[i][j] / alp;

          //第二个点
          vertices[k + 3] = i + 1 - wid2;
          vertices[k + 4] = j - hei2;
          vertices[k + 5] = 0;
          ncolors[k + 3] = mat[i + 1][j] / alp;
          ncolors[k + 4] = mat[i + 1][j] / alp;
          ncolors[k + 5] = mat[i + 1][j] / alp;

          //第三个点
          vertices[k + 6] = i - wid2;
          vertices[k + 7] = j + 1 - hei2;
          vertices[k + 8] = 0;
          ncolors[k + 6] = mat[i][j + 1] / alp;
          ncolors[k + 7] = mat[i][j + 1] / alp;
          ncolors[k + 8] = mat[i][j + 1] / alp;

          //第二个三角形
          //第一个点
          vertices[k + 9] = i + 1 - wid2;
          vertices[k + 10] = j + 1 - hei2;
          vertices[k + 11] = 0;
          ncolors[k + 9] = mat[i + 1][j + 1] / alp;
          ncolors[k + 10] = mat[i + 1][j + 1] / alp;
          ncolors[k + 11] = mat[i + 1][j + 1] / alp;

          //第二个点
          vertices[k + 12] = i - wid2;
          vertices[k + 13] = j + 1 - hei2;
          vertices[k + 14] = 0;
          ncolors[k + 12] = mat[i][j + 1] / alp;
          ncolors[k + 13] = mat[i][j + 1] / alp;
          ncolors[k + 14] = mat[i][j + 1] / alp;

          //第三个点
          vertices[k + 15] = i + 1 - wid2;
          vertices[k + 16] = j - hei2;
          vertices[k + 17] = 0;
          ncolors[k + 15] = mat[i + 1][j] / alp;
          ncolors[k + 16] = mat[i + 1][j] / alp;
          ncolors[k + 17] = mat[i + 1][j] / alp;

          k += 18;
        }
      }

      this.view.geometry.setAttribute(
        "position",
        new THREE.BufferAttribute(vertices, 3)
      );
      this.view.geometry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
      this.view.mesh.scale.set(this.mat_row_spacing, this.mat_col_spacing);
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
    matting_rm(mat, row, col, alp) {
      //删除fusion的效果
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
  computed: {
    scale_state() {
      return this.$store.getters.scale_state;
    },
  },

  watch: {
    p_mat(new_m, old_m) {
      if (new_m != undefined) {
        // console.log(new_m);
        this.mat_width = new_m.length;
        this.mat_height = new_m[0].length;
        if(this.label == 'z'){
          this.mat = this.reverse_mat(new_m);
        }
        else{
          this.mat = new_m;
        } 
        this.imgAdd(this.mat, this.alpha);
      }
    },
    label(new_label, old_label) {
      // if (new_label == "z" && old_label == "x" && this.init_finish) {
      //   this.view.mesh.rotateZ(Math.PI / 2);
      // } else if (new_label == "z" && old_label == "y" && this.init_finish) {
      //   this.view.mesh.rotateZ(Math.PI / 2);

      // }
      if ((new_label = "z" && old_label != "z")) {
        // this.view.mesh.rotateZ(-Math.PI / 2);
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

    scale_state(new_scale_state) {
      if (new_scale_state == 1) {
        if (this.mat != undefined) {
          this.scale_init();
          // this.container.removeEventListener("click", this.click, false);
          this.container.addEventListener("click", this.scale_operate);
          // document.addEventListener("keydown", this.scale_operate);
        }
      }
      else if(new_scale_state == 0){
        this.remove_scale();
      }
    },
  },
};
</script>