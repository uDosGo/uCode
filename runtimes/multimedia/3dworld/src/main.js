/**
 * uCode4 3dWorld — Three.js/WebGL frontend
 * Renders uCode4 worlds and scenes in the browser.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export class WorldRenderer {
  constructor(container) {
    this.container = container;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.controls = null;
    this.objects = new Map();
    this.animating = false;

    this._init();
  }

  _init() {
    // Renderer
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.shadowMap.enabled = true;
    this.container.appendChild(this.renderer.domElement);

    // Camera
    this.camera.position.set(0, 5, 15);
    this.camera.lookAt(0, 0, 0);

    // Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    this.scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    this.scene.add(directionalLight);

    const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3);
    fillLight.position.set(-10, 0, -10);
    this.scene.add(fillLight);

    // Grid helper
    const gridHelper = new THREE.GridHelper(50, 20, 0x444466, 0x333355);
    this.scene.add(gridHelper);

    // Handle resize
    window.addEventListener('resize', () => this._onResize());
  }

  _onResize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  /**
   * Load a world from uCode4 scene data.
   * @param {Object} sceneData - Scene data from uCode4 Python backend
   */
  loadScene(sceneData) {
    // Clear existing objects
    for (const [id, obj] of this.objects) {
      this.scene.remove(obj);
    }
    this.objects.clear();

    if (!sceneData || !sceneData.objects) return;

    for (const objData of sceneData.objects) {
      this._addObject(objData);
    }
  }

  _addObject(objData) {
    const pos = objData.position || [0, 0, 0];
    let mesh;

    switch (objData.type) {
      case 'sprite':
      case 'bob':
        mesh = new THREE.Mesh(
          new THREE.BoxGeometry(1, 1, 1),
          new THREE.MeshStandardMaterial({ color: 0x44aaff })
        );
        break;
      case 'model':
        mesh = new THREE.Mesh(
          new THREE.SphereGeometry(0.8, 16, 16),
          new THREE.MeshStandardMaterial({ color: 0xff8844 })
        );
        break;
      case 'light':
        const light = new THREE.PointLight(0xffffaa, 1, 20);
        light.position.set(pos[0], pos[1], pos[2]);
        this.scene.add(light);
        this.objects.set(objData.object_id || objData.name, light);
        return;
      case 'text':
      default:
        mesh = new THREE.Mesh(
          new THREE.PlaneGeometry(2, 1),
          new THREE.MeshStandardMaterial({ color: 0x88ff88, transparent: true, opacity: 0.7 })
        );
        break;
    }

    if (mesh) {
      mesh.position.set(pos[0], pos[1], pos[2]);
      if (objData.rotation) {
        mesh.rotation.set(
          THREE.MathUtils.degToRad(objData.rotation[0] || 0),
          THREE.MathUtils.degToRad(objData.rotation[1] || 0),
          THREE.MathUtils.degToRad(objData.rotation[2] || 0)
        );
      }
      if (objData.scale) {
        mesh.scale.set(objData.scale[0] || 1, objData.scale[1] || 1, objData.scale[2] || 1);
      }
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      this.scene.add(mesh);
      this.objects.set(objData.object_id || objData.name, mesh);
    }
  }

  setBackgroundColor(color) {
    this.scene.background = new THREE.Color(color);
  }

  start() {
    this.animating = true;
    this._animate();
  }

  stop() {
    this.animating = false;
  }

  _animate() {
    if (!this.animating) return;
    requestAnimationFrame(() => this._animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}

// Auto-initialize if running in browser
if (typeof window !== 'undefined' && document.getElementById('ucode4-viewport')) {
  const container = document.getElementById('ucode4-viewport');
  const renderer = new WorldRenderer(container);
  renderer.setBackgroundColor('#1a1a2e');
  renderer.start();
}
