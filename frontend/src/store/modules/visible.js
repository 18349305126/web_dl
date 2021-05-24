const state = {
    result_view_state : 0,//0表示默认体渲染，1表示fusion，2表示标签标记
    fusion_states : [-1,-1,-1,-1],
    visible_states: [true,true,true],
    scale_state: 0, //0表示放大镜功能未启用，1表示放大镜功能启用
}

const mutations = {
    RESET_RESULT_VIEW_STATE :(state,result_view_state) => {
        state.result_view_state = result_view_state;
    },
    RESET_FUSION_STATES:(state,fusion_states) =>{
        state.fusion_states = fusion_states;
    },
    RESET_VISIBLE_STATES:(state, visible_states)=>{
        state.visible_states = visible_states;
    },
    RESET_SCALE_STATE:(state, scale_state)=>{
        state.scale_state = scale_state;
    },
}

const actions = {
    
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
}