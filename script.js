// script.js — исправленная версия с синхронизированным поворотом

let scene, camera, renderer, raycaster, mouse;
let previewScene, previewCamera, previewRenderer;
let previewTileGroup = null;

let players = [];
let gameState = { scores: {}, turn: 0 };
let quizState = null;
let highlightMesh = null;
let placedHexes = {};
let currentTileRotation = 0;
let currentTileType = null;

let isDragging = false;
let prevMouse = { x: 0, y: 0 };
let camPos = { x: 0, z: 0 };
let camHeight = 35;

const TILE_TYPES = [
    { sides: ['field', 'city', 'road', 'field', 'city', 'road'], name: 'Tile 1' },
    { sides: ['city', 'road', 'field', 'city', 'road', 'field'], name: 'Tile 2' },
    { sides: ['road', 'road', 'road', 'road', 'road', 'road'], name: 'Road Cross' },
    { sides: ['city', 'city', 'city', 'field', 'field', 'field'], name: 'Big City' },
    { sides: ['field', 'field', 'field', 'road', 'road', 'road'], name: 'Tile 5' }
];

const SIDE_COLORS = {
    city: 0xFF6B00,
    road: 0x95A5A6,
    field: 0x2ECC71
};

const PLAYER_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'];

const QUESTIONS = [
    { q: "Столица Франции?", a: ["Париж", "Лондон", "Берлин", "Мадрид"], c: 0 },
    { q: "Планета ближе к Солнцу?", a: ["Меркурий", "Венера", "Земля", "Марс"], c: 0 },
    { q: "Континентов на Земле?", a: ["5", "6", "7", "8"], c: 2 }
];

const HEX_RADIUS = 1;
const HEX_HEIGHT = Math.sqrt(3) * HEX_RADIUS;

const DIRECTIONS = [
    [ 1,  0], [ 1, -1], [ 0, -1],
    [-1,  0], [-1,  1], [ 0,  1]
];

function hexToKey(q, r) { return `${q},${r}`; }

function hexToWorld(q, r) {
    return {
        x: HEX_RADIUS * 1.5 * q,
        z: HEX_HEIGHT * (r + q / 2)
    };
}

function worldToHex(x, z) {
    let q = (2/3 * x) / HEX_RADIUS;
    let r = (-1/3 * x + Math.sqrt(3)/3 * z) / HEX_RADIUS;
    return hexRound(q, r);
}

function hexRound(q, r) {
    let s = -q - r;
    let rq = Math.round(q), rr = Math.round(r), rs = Math.round(s);
    let qdiff = Math.abs(rq - q), rdiff = Math.abs(rr - r), sdiff = Math.abs(rs - s);
    if (qdiff > rdiff && qdiff > sdiff) rq = -rr - rs;
    else if (rdiff > sdiff) rr = -rq - rs;
    return { q: rq, r: rr };
}

// ОБРАТНЫЙ ПОВОРОТ - для визуализации
function getRotatedSidesForVisualization(sides, rot) {
    rot = rot % 6;
    if (rot === 0) return [...sides];
    // Для визуализации: поворот против часовой стрелки
    return sides.map((_, i) => sides[(i + rot) % 6]);
}

// ОБРАТНЫЙ ПОВОРОТ - для получения типа сегмента
function getSegmentTypeForVisualization(sides, rotation, segmentIndex) {
    return sides[(segmentIndex + rotation) % 6];
}

// ПРЯМОЙ ПОВОРОТ - для логики размещения
function getRotatedSidesForLogic(sides, rot) {
    rot = rot % 6;
    if (rot === 0) return [...sides];
    // Для логики: поворот по часовой стрелке
    return sides.map((_, i) => sides[(i - rot + 6) % 6]);
}

function isAdjacent(q, r) {
    for (let [dq, dr] of DIRECTIONS) {
        if (placedHexes[hexToKey(q + dq, r + dr)]) return true;
    }
    return false;
}

// Используем ПРЯМОЙ поворот для логики
function matchesNeighborsSoft(q, r, sides, rotation) {
    const rotated = getRotatedSidesForLogic(sides, rotation);
    
    for (let i = 0; i < 6; i++) {
        let [dq, dr] = DIRECTIONS[i];
        let key = hexToKey(q + dq, r + dr);
        
        if (placedHexes[key]) {
            let n = placedHexes[key];
            let nRotated = getRotatedSidesForLogic(n.sides, n.rotation);
            
            let neighborSideIndex = (i + 3) % 6;
            
            console.log(`Проверка направления ${i}:`);
            console.log(`  Наш тайл сторона ${i} = ${rotated[i]}`);
            console.log(`  Сосед сторона ${neighborSideIndex} = ${nRotated[neighborSideIndex]}`);
            
            if (rotated[i] !== nRotated[neighborSideIndex]) {
                console.log(`  НЕ СОВПАДАЕТ!`);
                return false;
            }
            console.log(`  Совпадает ✓`);
        }
    }
    return true;
}

function updatePlacementGrid() {
    scene.children.filter(c => c.userData && c.userData.isPlacementGrid).forEach(c => scene.remove(c));

    if (!currentTileType) return;

    const possible = new Set();

    Object.keys(placedHexes).forEach(key => {
        const [q, r] = key.split(',').map(Number);
        DIRECTIONS.forEach(([dq, dr]) => {
            const nq = q + dq;
            const nr = r + dr;
            const nkey = hexToKey(nq, nr);
            if (!placedHexes[nkey]) possible.add(nkey);
        });
    });

    possible.forEach(key => {
        const [q, r] = key.split(',').map(Number);
        const pos = hexToWorld(q, r);

        const outline = createHexOutline();
        const canPlace = matchesNeighborsSoft(q, r, currentTileType.sides, currentTileRotation);
        const color = canPlace ? 0x44ff88 : 0xff5555;

        const mat = new THREE.LineBasicMaterial({
            color,
            linewidth: 6,
            transparent: true,
            opacity: 0.9
        });

        const mesh = new THREE.LineLoop(outline, mat);
        mesh.position.set(pos.x, 0.08, pos.z);
        mesh.userData.isPlacementGrid = true;
        scene.add(mesh);
    });
}

function updateCamera() {
    camera.position.set(camPos.x, camHeight, camPos.z);
    camera.lookAt(camPos.x, 0, camPos.z);
}

function startDrag(e) {
    if (e.button !== 0) return;
    if (quizState || document.getElementById('menu').style.display !== 'none') return;
    isDragging = true;
    prevMouse.x = e.clientX;
    prevMouse.y = e.clientY;
    e.preventDefault();
}

function stopDrag() {
    isDragging = false;
}

function moveDrag(e) {
    if (!isDragging) return;

    const dx = (e.clientX - prevMouse.x) * 0.12;
    const dy = (e.clientY - prevMouse.y) * 0.12;

    camPos.x -= dx;
    camPos.z += dy;

    updateCamera();

    prevMouse.x = e.clientX;
    prevMouse.y = e.clientY;
}

function init3D() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a15);

    camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 2000);
    updateCamera();

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(innerWidth, innerHeight);
    document.getElementById('game-container').appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.65));
    let dl = new THREE.DirectionalLight(0xffffff, 1.2);
    dl.position.set(18,35,22); scene.add(dl);

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    let outline = createHexOutline();
    highlightMesh = new THREE.LineLoop(outline, new THREE.LineBasicMaterial({
        color: 0xffff00,
        linewidth: 5
    }));
    highlightMesh.position.y = 0.04;
    highlightMesh.visible = false;
    scene.add(highlightMesh);

    initPreview();

    window.addEventListener('resize', () => {
        camera.aspect = innerWidth / innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(innerWidth, innerHeight);
    });

    window.addEventListener('keydown', e => {
        if (quizState) return;
        if (e.key.toLowerCase() === 'r') {
            rotateTile();
            updatePlacementGrid();
        }
    });

    renderer.domElement.addEventListener('mousedown', startDrag);
    renderer.domElement.addEventListener('mouseup', stopDrag);
    renderer.domElement.addEventListener('mouseleave', stopDrag);
    window.addEventListener('mouseup', stopDrag);
    renderer.domElement.addEventListener('mousemove', moveDrag);

    renderer.domElement.addEventListener('wheel', e => {
        e.preventDefault();
        if (quizState || document.getElementById('menu').style.display !== 'none') return;

        const delta = e.deltaY > 0 ? 3 : -3;
        camHeight = Math.max(12, Math.min(80, camHeight + delta));
        updateCamera();
    }, { passive: false });

    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('click', onClick);

    animate();
}

function onMouseMove(e) {
    if (document.getElementById('menu').style.display !== 'none' || quizState) return;

    mouse.x = (e.clientX / innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0.1);
    const intersectPoint = new THREE.Vector3();

    if (raycaster.ray.intersectPlane(plane, intersectPoint)) {
        if (intersectPoint.length() > 300) return;

        const hex = worldToHex(intersectPoint.x, intersectPoint.z);
        const key = hexToKey(hex.q, hex.r);
        const pos = hexToWorld(hex.q, hex.r);

        highlightMesh.position.set(pos.x, 0.04, pos.z);

        if (placedHexes[key] || !isAdjacent(hex.q, hex.r)) {
            highlightMesh.visible = false;
        } else {
            const valid = matchesNeighborsSoft(hex.q, hex.r, currentTileType?.sides || [], currentTileRotation);
            highlightMesh.material.color.set(valid ? 0x44ff88 : 0xff5555);
            highlightMesh.visible = true;
        }
    } else {
        highlightMesh.visible = false;
    }
}

function onClick(e) {
    if (document.getElementById('menu').style.display !== 'none' || quizState) return;

    mouse.x = (e.clientX / innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const plane = new THREE.Plane(new THREE.Vector3(0,1,0), 0.1);
    const pt = new THREE.Vector3();
    if (!raycaster.ray.intersectPlane(plane, pt)) return;

    const hex = worldToHex(pt.x, pt.z);
    placeTile(hex.q, hex.r);
}

function initPreview() {
    const cont = document.getElementById('tile-preview');
    if (!cont) return console.error("tile-preview not found");

    previewScene = new THREE.Scene();
    previewScene.background = new THREE.Color(0x222233);

    previewCamera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    previewCamera.position.set(0, 5.5, 10.5);
    previewCamera.lookAt(0, 0.8, 0);

    previewRenderer = new THREE.WebGLRenderer({ antialias: true });
    previewRenderer.setSize(260, 260);
    previewRenderer.setClearColor(0x1a1a2e, 1);
    cont.appendChild(previewRenderer.domElement);

    previewScene.add(new THREE.AmbientLight(0xffffff, 1.2));
    const dirLight = new THREE.DirectionalLight(0xffffff, 2.0);
    dirLight.position.set(8, 12, 10);
    previewScene.add(dirLight);
}

function updatePreview() {
    while (previewScene.children.length > 2) {
        previewScene.remove(previewScene.children[previewScene.children.length - 1]);
    }

    if (!currentTileType) return;

    // Используем ОБРАТНЫЙ поворот для визуализации
    previewTileGroup = createHexWithSides(0, 0, currentTileType.sides, currentTileRotation, true);
    previewTileGroup.position.y = 0.3;
    previewScene.add(previewTileGroup);
}

function createHexOutline() {
    let pts = [];
    for (let i = 0; i < 6; i++) {
        let a = i * Math.PI / 3;
        pts.push(new THREE.Vector3(HEX_RADIUS * Math.cos(a), 0, HEX_RADIUS * Math.sin(a)));
    }
    pts.push(pts[0]); // замыкаем

    return new THREE.BufferGeometry().setFromPoints(pts);
}

function createHexWithSides(q, r, sides, rotation, isPreview = false) {
    let group = new THREE.Group();

    let inner = HEX_RADIUS * 0.38;
    let shape = new THREE.Shape();
    for (let i = 0; i < 6; i++) {
        let a = i * Math.PI / 3;
        let x = inner * Math.cos(a), y = inner * Math.sin(a);
        i === 0 ? shape.moveTo(x,y) : shape.lineTo(x,y);
    }
    shape.closePath();

    let geo = new THREE.ExtrudeGeometry(shape, {depth:0.45, bevelEnabled:false});
    let mat = new THREE.MeshPhongMaterial({color: 0x222233});
    let center = new THREE.Mesh(geo, mat);
    center.rotation.x = -Math.PI/2;
    group.add(center);

    for (let i = 0; i < 6; i++) {
        let a1 = i * Math.PI / 3;
        let a2 = (i+1) * Math.PI / 3;

        let s = new THREE.Shape();
        s.moveTo(inner * Math.cos(a1), inner * Math.sin(a1));
        s.lineTo(HEX_RADIUS * Math.cos(a1), HEX_RADIUS * Math.sin(a1));
        s.lineTo(HEX_RADIUS * Math.cos(a2), HEX_RADIUS * Math.sin(a2));
        s.lineTo(inner * Math.cos(a2), inner * Math.sin(a2));
        s.closePath();

        // Используем ОБРАТНЫЙ поворот для визуализации
        const segType = getSegmentTypeForVisualization(sides, rotation, i);
        let sideGeo = new THREE.ExtrudeGeometry(s, {depth:0.45, bevelEnabled:false});
        let sideMat = new THREE.MeshPhongMaterial({color: SIDE_COLORS[segType]});
        let side = new THREE.Mesh(sideGeo, sideMat);
        side.rotation.x = -Math.PI/2;
        group.add(side);
        
        // Добавляем номера сторон для отладки
        if (isPreview) {
            const canvas = document.createElement('canvas');
            canvas.width = 64;
            canvas.height = 64;
            const context = canvas.getContext('2d');
            context.fillStyle = 'white';
            context.font = '20px Arial';
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillText(i.toString(), 32, 32);
            
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.scale.set(0.25, 0.25, 1);
            
            const midAngle = (i + 0.5) * Math.PI / 3;
            const labelRadius = HEX_RADIUS * 0.6;
            sprite.position.set(
                labelRadius * Math.cos(midAngle),
                0.5,
                labelRadius * Math.sin(midAngle)
            );
            group.add(sprite);
        }
    }

    if (!isPreview) {
        let pos = hexToWorld(q, r);
        group.position.set(pos.x, 0, pos.z);
    }

    return group;
}

function animate() {
    requestAnimationFrame(animate);

    if (previewTileGroup && previewRenderer && previewScene && previewCamera) {
        previewRenderer.render(previewScene, previewCamera);
    }

    renderer.render(scene, camera);
}

function rotateTile() {
    if (quizState) return;
    currentTileRotation = (currentTileRotation + 1) % 6;
    console.log(`=== ПОВОРОТ ТАЙЛА: ${currentTileRotation} ===`);
    console.log(`Исходные стороны: ${currentTileType.sides.join(', ')}`);
    console.log(`Для визуализации (preview): ${getRotatedSidesForVisualization(currentTileType.sides, currentTileRotation).join(', ')}`);
    console.log(`Для логики (размещение): ${getRotatedSidesForLogic(currentTileType.sides, currentTileRotation).join(', ')}`);
    updatePreview();
    updatePlacementGrid();
}

function generateNewTile() {
    currentTileType = TILE_TYPES[Math.floor(Math.random() * TILE_TYPES.length)];
    currentTileRotation = 0;
    console.log(`=== НОВЫЙ ТАЙЛ: ${currentTileType.name} ===`);
    console.log(`Исходные стороны: ${currentTileType.sides.join(', ')}`);
    console.log(`Для визуализации (preview): ${getRotatedSidesForVisualization(currentTileType.sides, 0).join(', ')}`);
    console.log(`Для логики (размещение): ${getRotatedSidesForLogic(currentTileType.sides, 0).join(', ')}`);
    updatePreview();
    updatePlacementGrid();
}

function addPlayer() {
    let name = document.getElementById('name').value.trim();
    if (!name) return;
    players.push({
        id: Date.now(),
        name,
        color: PLAYER_COLORS[players.length % PLAYER_COLORS.length]
    });
    document.getElementById('name').value = '';
    updatePlayers();
}

function updatePlayers() {
    let html = players.map(p => `
        <div class="player">
            <div class="color-dot" style="background:${p.color}"></div>
            <span>${p.name}</span>
        </div>
    `).join('');
    document.getElementById('players').innerHTML = html;
}

function startGame() {
    if (players.length < 2) return alert('Минимум 2 игрока');
    gameState.scores = {}; players.forEach(p => gameState.scores[p.id] = 0);
    gameState.turn = 0; placedHexes = {};

    document.getElementById('menu').style.display = 'none';
    document.getElementById('game-ui').style.display = 'block';

    let start = {sides: Array(6).fill('field')};
    let hex = createHexWithSides(0,0, start.sides, 0, false);
    scene.add(hex);
    placedHexes[hexToKey(0,0)] = {sides: start.sides, rotation: 0};

    console.log('Игра начата, начальный тайл размещен');
    
    generateNewTile();
    updatePlacementGrid();
    updateScores();
}

function updateScores() {
    let html = players.map(p => `
        <div class="score">
            <div><span style="color:${p.color}">●</span> ${p.name}</div>
            <span>${gameState.scores[p.id] || 0}</span>
        </div>
    `).join('');
    document.getElementById('scores').innerHTML = html;
}

function placeTile(q, r) {
    let key = hexToKey(q, r);
    if (placedHexes[key]) {
        console.log('Клетка уже занята');
        return;
    }
    
    // Первый тайл можно размещать без соседей
    if (Object.keys(placedHexes).length > 0 && !isAdjacent(q, r)) {
        console.log('Тайл должен быть размещен рядом с существующим тайлом');
        return;
    }
    
    console.log(`=== Пытаемся разместить тайл на (${q},${r}) ===`);
    console.log(`Тип тайла: ${currentTileType?.name}`);
    console.log(`Исходные стороны: ${currentTileType?.sides?.join(', ')}`);
    console.log(`Поворот: ${currentTileRotation}`);
    console.log(`Для логики (размещение): ${getRotatedSidesForLogic(currentTileType.sides, currentTileRotation).join(', ')}`);
    
    if (!matchesNeighborsSoft(q, r, currentTileType.sides, currentTileRotation)) {
        console.log('Не совпадают с соседями!');
        return;
    }

    let hex = createHexWithSides(q, r, currentTileType.sides, currentTileRotation, false);
    scene.add(hex);
    placedHexes[key] = {
        sides: currentTileType.sides, 
        rotation: currentTileRotation, 
        type: currentTileType.name,
        // Сохраняем обе версии для отладки
        sidesVisual: getRotatedSidesForVisualization(currentTileType.sides, currentTileRotation),
        sidesLogic: getRotatedSidesForLogic(currentTileType.sides, currentTileRotation)
    };

    console.log(`Тайл успешно размещен на (${q},${r})!`);
    
    gameState.turn++;
    document.getElementById('turn').textContent = gameState.turn;

    generateNewTile();
    updatePlacementGrid();

    if (Math.random() > 0.6) startQuiz();
}

function startQuiz() {
    let qs = Array(3).fill().map(() => QUESTIONS[Math.floor(Math.random()*QUESTIONS.length)]);
    quizState = {
        questions: qs,
        current: 0,
        answers: {},
        points: 5 + Math.floor(Math.random()*16)
    };
    players.forEach(p => quizState.answers[p.id] = 0);
    showQuiz();
}

function showQuiz() {
    document.getElementById('quiz').style.display = 'block';
    let q = quizState.questions[quizState.current];
    document.getElementById('pts').textContent = quizState.points;
    document.getElementById('qnum').textContent = quizState.current + 1;
    document.getElementById('question').textContent = q.q;

    let html = '';
    q.a.forEach((ans,i) => {
        players.forEach(p => {
            html += `<button class="ans-btn" style="background:${p.color}22;border-left:5px solid ${p.color}" onclick="answer(${p.id},${i})">${p.name}: ${ans}</button>`;
        });
    });
    document.getElementById('answers').innerHTML = html;
}

window.answer = function(pid, idx) {
    let q = quizState.questions[quizState.current];
    if (idx === q.c) quizState.answers[pid]++;
    if (quizState.current < 2) {
        quizState.current++;
        showQuiz();
    } else finishQuiz();
};

function finishQuiz() {
    let max = Math.max(...Object.values(quizState.answers));
    let winners = Object.keys(quizState.answers).filter(id => quizState.answers[id] === max);
    let pts = winners.length > 1 ? Math.floor(quizState.points / winners.length) : quizState.points;
    winners.forEach(id => gameState.scores[id] += pts);
    updateScores();
    document.getElementById('quiz').style.display = 'none';
    quizState = null;
}

function endGame() {
    let max = -1, winId = null;
    for (let [id,sc] of Object.entries(gameState.scores)) {
        if (sc > max) { max = sc; winId = id; }
    }
    let winner = players.find(p => p.id == winId);
    alert(`Победитель: ${winner.name} — ${max} очков!`);

    scene.children = [];
    scene.add(new THREE.AmbientLight(0xffffff, 0.65));
    let dl = new THREE.DirectionalLight(0xffffff, 1.2);
    dl.position.set(18,35,22); scene.add(dl);
    scene.add(highlightMesh);

    document.getElementById('menu').style.display = 'block';
    document.getElementById('game-ui').style.display = 'none';
    players = [];
    updatePlayers();
}

document.getElementById('name').addEventListener('keypress', e => {
    if (e.key === 'Enter') addPlayer();
});

init3D();
