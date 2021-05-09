<template>
  <div ref="information">
    <!-- <div class="window" v-if="this.information0.active == true">
      <InformationDetail v-bind:information="information0"> </InformationDetail>
    </div> -->
    <div class="window" v-if="this.information0.active == true">
      <InformationDetail v-bind:information="information0"> </InformationDetail>
      <!-- <div>
        <span>name:{{information0.name}}</span>
        <span>size:{{information0.width}} * {{information0.height}} </span>
      </div> -->
    </div>
    <div class="window" v-if="this.information1.active == true">
      <InformationDetail v-bind:information="information1"> </InformationDetail>
      <!-- <div>
        <span>name:{{information0.name}}</span>
        <span>size:{{information0.width}} * {{information0.height}} </span>
      </div> -->
    </div>
    <div class="window" v-if="this.information2.active == true">
      <InformationDetail v-bind:information="information2"> </InformationDetail>
      <!-- <div>
        <span>name:{{information0.name}}</span>
        <span>size:{{information0.width}} * {{information0.height}} </span>
      </div> -->
    </div>
  </div>
</template>

<script type="text/javascript">
import InformationDetail from "./InformationDetail";
export default {
  name: "Information",
  props: ["information0", "information1", "information2"],
  data() {
    return {};
  },
  components: { InformationDetail },

  created() {},
  mounted() {
    // console.log(this.information0.active);
    // console.log(document.getElementById("test11"));
    // document.getElementById("test11").addEventListener("click",(e)=>{
    //   console.log(this.information0)
    // })
  },

  computed: {
    // infor:()=>{
    //   return this.informations
    // }
  },
  watch: {
    information0(new_i) {
      // console.log(new_i);
    },
    information1(new_i){
      console.log(new_i)
    }
  },
};
</script>


