<template>
  <div>
    <div ref="container_canv"></div>
  </div>
</template>

<script>
import * as THREE from "three";
import Vue from "vue";
// import { CSS2DRenderer, CSS2DObject } from "three-css2drender";
// import { BufferGeometry, Material, MeshBasicMaterial } from "three";
import axios from "axios";
// import * as cornerstone from "cornerstone-core";
// import * as dicomParser from "dicom-parser";
 
// // 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼 
// import * as cornerstoneWADOImageLoader from "../../static/dist/cornerstoneWADOImageLoader.js";
 
//指定要注册加载程序的基石实例
// cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
// import VueAxios from 'vue-axios';
// require("three/examples/js/loaders/VTKLoader");

const OrbitControls = require("three-orbit-controls")(THREE);

Vue.prototype.$Three = THREE;

export default {
  name: "VolumeRenderWindow",
  props:["width","height","vers","normals"],
  data() {
    return {
      control:{//控制相机的参数，有一些参数必须是全局变量
        speed_scale:Number,
        speed_rotate:Number,

        spher:{
          r:Number,
          theta:Number,
          pi:Number,
        },
        rect:{
          x:Number,
          y:Number,
          z:Number,
        },
        
      },

      container:"",
      scene: "",
      light: "",
      camera: "",
      // controls: "",
      renderer: "",
      geometry: "",
      fov: 80,

      img: "",
      // vers: Array,
      // normals: Array,
    };
  },
  created(){
    this.control.speed_scale = 10;
    this.control.speed_rotate = 0.002;

    this.control.rect.x = 10;
    this.control.rect.y = 10;
    this.control.rect.z = 100;//初始相机位置

    let sp_coord = this.get_spher_coord(this.control.rect.x,this.control.rect.y,this.control.rect.z);
    this.control.spher.r = sp_coord.r;
    this.control.spher.theta = sp_coord.theta;
    this.control.spher.pi = sp_coord.pi;

    
  },
  mounted() {
    this.initRender();
    // this.control_init();
    // this.read_data("../../../static/model/test/json_test.json","../../../static/model/test/normal_test.json");

    this.container.addEventListener("mousewheel",this.mousewheel,false);
    this.container.addEventListener("mousedown", this.mousedown, false);

    if(this.vers!=undefined && this.normals != undefined){
      this.addObj();
    }


    // this.container.addEventListener("mouseover", this.mouseover, false);
    // this.container.addEventListener("mouseout", this.mouseout, false);


  },

  methods: {
    initRender() {
      this.scene = new THREE.Scene();
      this.scene.add(new THREE.AmbientLight(0xdddddd,0.1)); //环境光

      // this.light = new THREE.DirectionalLight(0xff0000, 1); //
      
      // this.light = new THREE.PointLight(0xeeeeee, 1, 0);
      // this.light.position.set(10, 10, 200);
      // // this.light.position.multiplyScalar(0.3);
      // this.light.position.multiplyScalar(1);
      // this.scene.add(this.light);

      let light0 = new THREE.PointLight(0xeeeeee, 1, 0);
      light0.position.set(10, 10, 200);
      // this.light.position.multiplyScalar(0.3);
      light0.position.multiplyScalar(1);
      this.scene.add(light0);

      let light1 = new THREE.PointLight(0xeeeeee, 1, 0);
      light1.position.set(-10, -10, -200);
      // this.light.position.multiplyScalar(0.3);
      light1.position.multiplyScalar(1);
      this.scene.add(light1);


      this.camera = new THREE.PerspectiveCamera(
        75,
        this.width / this.height,
        0.1,
        1500
      );
      this.camera.position.set(this.control.rect.x , this.control.rect.y, this.control.rect.z);
      this.camera.lookAt(this.scene.position);

      // this.controls = new OrbitControls(this.camera);
      // this.controls.target.set(0, 0, 0);
      // this.controls.minDistance = 80;
      // this.controls.maxDistance = 400;
      // this.controls.maxPolarAngle = Math.PI / 3;
      // this.controls.update();

      this.renderer = new THREE.WebGLRenderer();
      this.renderer.setSize(this.width, this.height);

      this.container = this.$refs.container_canv;
      // const container = document.getElementById("dicomImage");
      this.container.appendChild(this.renderer.domElement);
      // this.container.addEventListener("mousewheel", this.mousewheel, false);
      // this.container.addEventListener("mousedown", this.mousedown, false);


      this.geometry = new THREE.BufferGeometry();
      let material = new THREE.MeshLambertMaterial({
        color: 0xffffff,
        wireframe: false,
      });

      this.mesh = new THREE.Mesh(this.geometry, material);

      this.scene.add(this.mesh);
      this.render();

    },
    render() {
      requestAnimationFrame(this.render);
      this.renderer.render(this.scene, this.camera);
    },

    // read_data(data_url,normal_url) {
    //   axios.get(data_url).then((response) => {
    //     this.vers = new Float32Array(response.data);
    //   });
    //   axios.get(normal_url).then((response) => {
    //     this.normals = new Float32Array(response.data);
    //   });
    // },

    addObj() {
      this.geometry.addAttribute(
        "position",
        new THREE.BufferAttribute(this.vers, 3)
      );

      this.geometry.addAttribute(
        "normal",
        new THREE.Float32BufferAttribute(this.normals, 3)
      );
      this.geometry.center();

    },

    mousewheel(e){
      e.preventDefault();
      //e.stopPropagation();
      this.scale(e);

    },
    mousedown(e){
      const _this = this;
      if (e.button == 0) {
        // this.mouse_down_rotate(e);
        this.mouse_move_rotate(e);
      }
      this.container.onmouseup = function (e) {
        _this.container.onmousemove = null;
        _this.container.onmouseup = null;
      };
    },

    mouse_down_rotate(e){//记录当前鼠标位置，从而判断之后的旋转情况
    	this.control.rotate_start.set( e.clientX, e.clientY );
    },

    mouse_move_rotate(e){//当鼠标开始移动的时候
      const _this = this;

      let ori_x = e.clientX;
      let ori_y = e.clientY;

      let old_theta = this.control.spher.theta;
      let old_pi = this.control.spher.pi;


      if (e.button == 0) {
          _this.container.onmousemove = function (e) {
          //计算需要移动的距离
          let dx = e.clientX - ori_x;
          let dy = e.clientY - ori_y;

          let new_theta = old_theta - dx * _this.control.speed_rotate;
          let new_pi = old_pi - dy * _this.control.speed_rotate;

          _this.control.spher.theta = new_theta;
          _this.control.spher.pi = new_pi;

          let rect_coord = _this.get_rect_coord(_this.control.spher.r,_this.control.spher.theta,_this.control.spher.pi);
          
          _this.camera.position.set(rect_coord.x,rect_coord.y,rect_coord.z);
          _this.camera.lookAt(_this.scene.position)

        };
      }
    },

    scale(e){
      if (e.wheelDelta) {
        //判断浏览器IE，谷歌滑轮事件
        if (e.wheelDelta > 0) {
          //当滑轮向上滚动时

          this.control.spher.r -= this.control.speed_scale;
        }
        if (e.wheelDelta < 0) {
          //当滑轮向下滚动时
          this.control.spher.r += this.control.speed_scale;
        }
      } else if (e.detail) {
        if (e.detail > 0) {
          //当滑轮向上滚动时
          this.control.spher.r -= this.control.speed_scale;

        }
        if (e.detail < 0) {
          //当滑轮向下滚动时
          this.control.spher.r += this.control.speed_scale;

        }
      }

      let rect_coord = this.get_rect_coord(this.control.spher.r,this.control.spher.theta,this.control.spher.pi);
      this.control.rect.x = rect_coord.x;
      this.control.rect.y = rect_coord.y;
      this.control.rect.z = rect_coord.z;
      this.camera.position.set(rect_coord.x,rect_coord.y,rect_coord.z);

    },

    get_rect_coord(r,theta,pi){
      let x = r* Math.sin(theta)*Math.cos(pi);
      let y = r* Math.sin(theta)*Math.sin(pi);
      let z = r* Math.cos(theta);
      return{x:x,y:y,z:z};
    },

    get_spher_coord(x,y,z){
      let r = Math.sqrt(x*x+y*y+z*z);
      let theta = Math.acos(z/r);
      let pi = Math.atan(y/x);
      return{r:r,theta:theta,pi:pi};
    }




    // mouseover(e){
    //   e.preventDefault();
    //   console.log("mouseon");
    //   this.control_on();

    // },
    // mouseout(e){
    //   e.preventDefault();
    //   console.log("mouseout");
    //   this.control_remove();
      
    // },
    // control_on(){
    //   this.controls.enable = true;
    //   this.enableZoom = true;
		//   this.enableRotate = true;
		//   this.enablePan = true;
    // },
    // control_init(){
    //   this.controls = new OrbitControls(this.camera);
    //   this.enableZoom = false;
    //   this.controls.target.set(0, 0, 0);
    //   this.controls.minDistance = 80;
    //   this.controls.maxDistance = 400;
    //   this.controls.maxPolarAngle = Math.PI / 3;
    //   this.controls.update();

    //   this.controls.enable = false;
    //   this.enableZoom = false;
		//   this.enableRotate = false;
		//   this.enablePan = false;

    // },
    // control_remove(){
    //   this.controls.enable = false;
    //   this.enableZoom = false;
		//   this.enableRotate = false;
		//   this.enablePan = false;    
    // },
    
  },
  watch:{
    vers(new_v,old_v){
      // console.log(new_v)
      this.addObj();
    },
    normals(new_n,old_n){
      // console.log(new_n)
      this.addObj();
    }
  }
};
</script>


