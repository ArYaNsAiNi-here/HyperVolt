'use client'

import { useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, useGLTF } from '@react-three/drei'
import * as THREE from 'three'

interface DigitalTwinProps {
  lightIntensity: number // 0-100 from LDR sensor
  activeSource: 'solar' | 'battery' | 'grid'
  brightnessThreshold: number // 0-100 user preference
  weatherCondition?: string // 'sunny', 'cloudy', 'rainy', etc.
  className?: string
}

// House model component with GLTF support
function HouseModel({ 
  lightIntensity, 
  brightnessThreshold,
  weatherCondition = 'sunny' 
}: { 
  lightIntensity: number
  brightnessThreshold: number
  weatherCondition: string
}) {
  const houseRef = useRef<THREE.Group>(null)
  const indoorLightRef = useRef<THREE.PointLight>(null)
  
  // Try to load GLTF model, fallback to basic house if not available
  let gltf: any = null
  try {
    gltf = useGLTF('/models/sus_room.glb')
  } catch (error) {
    console.log('GLTF model not found, using fallback')
  }

  // Calculate indoor light intensity based on user preference
  // User brightness threshold determines how much artificial light is needed
  const indoorLightIntensity = (brightnessThreshold / 100) * 1.5

  // Determine if it's "daytime" based on light sensor
  const isDaytime = lightIntensity > 30

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Update indoor light based on user preference
    if (indoorLightRef.current) {
      // Smooth transition for indoor lighting
      const targetIntensity = indoorLightIntensity + Math.sin(time * 2) * 0.05
      indoorLightRef.current.intensity = targetIntensity
    }

    // Gentle rotation for GLTF model
    if (houseRef.current && gltf) {
      houseRef.current.rotation.y = Math.sin(time * 0.2) * 0.1
    }
  })

  if (gltf) {
    // Render GLTF model
    return (
      <group ref={houseRef} position={[0, -0.8, 0]} scale={0.8}>
        <primitive object={gltf.scene} />
        
        {/* Indoor lighting based on user preference */}
        <pointLight
          ref={indoorLightRef}
          position={[0, 1, 0]}
          intensity={indoorLightIntensity}
          color="#FFE5B4"
          distance={4}
          decay={2}
        />
        
        {/* Additional lights for different rooms if needed */}
        <pointLight
          position={[-0.5, 0.8, 0.5]}
          intensity={indoorLightIntensity * 0.6}
          color="#FFE5B4"
          distance={2.5}
          decay={2}
        />
        <pointLight
          position={[0.5, 0.8, -0.5]}
          intensity={indoorLightIntensity * 0.6}
          color="#FFE5B4"
          distance={2.5}
          decay={2}
        />
      </group>
    )
  }

  // Fallback: Basic house model
  return (
    <group ref={houseRef} position={[0, -0.8, 0]}>
      {/* House base */}
      <mesh position={[0, 0.4, 0]}>
        <boxGeometry args={[1.2, 0.8, 1.2]} />
        <meshStandardMaterial 
          color="#2D3748"
          emissive="#3B82F6"
          emissiveIntensity={indoorLightIntensity * 0.3}
        />
      </mesh>
      {/* Roof */}
      <mesh position={[0, 1, 0]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[0.9, 0.6, 4]} />
        <meshStandardMaterial 
          color="#1F2937"
          emissive="#3B82F6"
          emissiveIntensity={indoorLightIntensity * 0.2}
        />
      </mesh>
      {/* Indoor light */}
      <pointLight
        ref={indoorLightRef}
        position={[0, 0.6, 0]}
        intensity={indoorLightIntensity}
        color="#FFE5B4"
        distance={3}
        decay={2}
      />
    </group>
  )
}

// Sunlight component that changes based on weather and time
function Sunlight({ 
  lightIntensity, 
  weatherCondition = 'sunny',
  activeSource 
}: { 
  lightIntensity: number
  weatherCondition: string
  activeSource: string
}) {
  const sunRef = useRef<THREE.DirectionalLight>(null)
  
  // Determine sunlight color and intensity based on weather
  const sunlightConfig = useMemo(() => {
    const isDaytime = lightIntensity > 20
    
    if (!isDaytime) {
      // Night time - no sunlight
      return { color: '#1a1a2e', intensity: 0.1 }
    }

    // Daytime sunlight based on weather
    switch (weatherCondition.toLowerCase()) {
      case 'sunny':
      case 'clear':
        return { 
          color: '#FFF4E0', // Warm sunny color
          intensity: Math.min(lightIntensity / 100 * 2, 1.5) 
        }
      case 'cloudy':
      case 'overcast':
        return { 
          color: '#E8E8E8', // Cool gray light
          intensity: Math.min(lightIntensity / 100 * 1.2, 0.8) 
        }
      case 'rainy':
      case 'rain':
        return { 
          color: '#C0C0D0', // Blue-ish gray
          intensity: Math.min(lightIntensity / 100 * 0.8, 0.5) 
        }
      case 'foggy':
      case 'fog':
        return { 
          color: '#D0D0D8', // Soft gray
          intensity: Math.min(lightIntensity / 100 * 0.6, 0.4) 
        }
      default:
        return { 
          color: '#FFF8DC', // Default warm light
          intensity: Math.min(lightIntensity / 100 * 1.5, 1.2) 
        }
    }
  }, [lightIntensity, weatherCondition])

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    if (sunRef.current) {
      // Simulate sun movement during the day
      const sunAngle = (lightIntensity / 100) * Math.PI
      sunRef.current.position.x = Math.cos(sunAngle) * 5
      sunRef.current.position.y = Math.max(Math.sin(sunAngle) * 5, 0.5)
      sunRef.current.position.z = Math.sin(sunAngle) * 2
      
      // Slight intensity variation for realism
      sunRef.current.intensity = sunlightConfig.intensity + Math.sin(time * 0.5) * 0.05
    }
  })

  return (
    <>
      {/* Directional sunlight */}
      <directionalLight
        ref={sunRef}
        color={sunlightConfig.color}
        intensity={sunlightConfig.intensity}
        position={[3, 4, 2]}
        castShadow
      />
      
      {/* Ambient light for general scene visibility */}
      <ambientLight intensity={0.3} color={sunlightConfig.color} />
      
      {/* Hemisphere light for sky/ground color variation */}
      <hemisphereLight
        color={sunlightConfig.color}
        groundColor="#2A2A2A"
        intensity={sunlightConfig.intensity * 0.5}
      />
    </>
  )
}

function Room({ 
  lightIntensity, 
  activeSource,
  brightnessThreshold,
  weatherCondition = 'sunny'
}: { 
  lightIntensity: number
  activeSource: string
  brightnessThreshold: number
  weatherCondition?: string
}) {
  const roomRef = useRef<THREE.Group>(null)

  // Source colors
  const sourceColors = {
    solar: '#FDB022', // Yellow for solar
    battery: '#FF6B35', // Orange for battery
    grid: '#EF4444', // Red for grid
  }

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Gentle pulsing effect based on active source
    if (roomRef.current) {
      const pulseFactor = Math.sin(time * 2) * 0.02 + 1
      roomRef.current.scale.set(pulseFactor, pulseFactor, pulseFactor)
    }
  })

  // Floor color based on power source
  const floorColor = sourceColors[activeSource as keyof typeof sourceColors] || sourceColors.grid

  return (
    <group ref={roomRef}>
      {/* Room walls - wireframe style */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(5, 3, 5)]} />
        <lineBasicMaterial color="#4A5568" transparent opacity={0.6} />
      </lineSegments>

      {/* Floor with source color */}
      <mesh position={[0, -1.5, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[5, 5]} />
        <meshStandardMaterial 
          color={floorColor}
          transparent 
          opacity={0.2}
          emissive={floorColor}
          emissiveIntensity={0.3}
        />
      </mesh>

      {/* House with GLTF model support, indoor lighting, and sunlight through windows */}
      <Suspense fallback={null}>
        <HouseModel 
          lightIntensity={lightIntensity}
          brightnessThreshold={brightnessThreshold}
          weatherCondition={weatherCondition}
        />
      </Suspense>

      {/* Weather-based sunlight */}
      <Sunlight 
        lightIntensity={lightIntensity}
        weatherCondition={weatherCondition}
        activeSource={activeSource}
      />

      {/* Power Source Representations */}
      <PowerSources activeSource={activeSource} />

      {/* Energy particles flowing from source to house */}
      <EnergyParticles activeSource={activeSource} />
    </group>
  )
}

function EnergyParticles({ activeSource }: { activeSource: string }) {
  const particlesRef = useRef<THREE.Points>(null)

  const sourceColors = {
    solar: '#FDB022',
    battery: '#FF6B35',
    grid: '#EF4444',
  }

  // Source positions for particle animation
  const sourcePositions = {
    solar: { x: -2.5, y: 0.5, z: 2.5 },
    battery: { x: 2.5, y: -0.5, z: 2.5 },
    grid: { x: 0, y: 0, z: -2.8 },
  }

  // Create particles that flow from source to house
  const particles = useMemo(() => {
    const count = 40
    const positions = new Float32Array(count * 3)
    
    const sourcePos = sourcePositions[activeSource as keyof typeof sourcePositions] || sourcePositions.grid
    
    for (let i = 0; i < count; i++) {
      // Start particles near the active source
      const t = i / count
      positions[i * 3] = sourcePos.x * (1 - t) // x - move toward center
      positions[i * 3 + 1] = sourcePos.y * (1 - t) + (Math.random() - 0.5) * 0.3 // y
      positions[i * 3 + 2] = sourcePos.z * (1 - t) // z - move toward center
    }
    
    return positions
  }, [activeSource])

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array
      const sourcePos = sourcePositions[activeSource as keyof typeof sourcePositions] || sourcePositions.grid
      
      for (let i = 0; i < positions.length; i += 3) {
        // Move particles from source toward house (center)
        const dx = -positions[i] * 0.02
        const dy = -positions[i + 1] * 0.02
        const dz = -positions[i + 2] * 0.02
        
        positions[i] += dx
        positions[i + 1] += dy
        positions[i + 2] += dz
        
        // Reset particle to source position when it reaches center
        const distanceFromCenter = Math.sqrt(
          positions[i] * positions[i] + 
          positions[i + 1] * positions[i + 1] + 
          positions[i + 2] * positions[i + 2]
        )
        
        if (distanceFromCenter < 0.8) {
          positions[i] = sourcePos.x + (Math.random() - 0.5) * 0.3
          positions[i + 1] = sourcePos.y + (Math.random() - 0.5) * 0.3
          positions[i + 2] = sourcePos.z + (Math.random() - 0.5) * 0.3
        }
      }
      
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })

  const particleColor = sourceColors[activeSource as keyof typeof sourceColors] || sourceColors.grid

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
          args={[particles, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        color={particleColor}
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  )
}

function PowerSources({ activeSource }: { activeSource: string }) {
  const solarRef = useRef<THREE.Group>(null)
  const batteryRef = useRef<THREE.Group>(null)
  const gridRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Pulse the active source
    if (activeSource === 'solar' && solarRef.current) {
      const scale = 1 + Math.sin(time * 3) * 0.1
      solarRef.current.scale.set(scale, scale, scale)
    }
    if (activeSource === 'battery' && batteryRef.current) {
      const scale = 1 + Math.sin(time * 3) * 0.1
      batteryRef.current.scale.set(scale, scale, scale)
    }
    if (activeSource === 'grid' && gridRef.current) {
      const scale = 1 + Math.sin(time * 3) * 0.1
      gridRef.current.scale.set(scale, scale, scale)
    }
  })

  return (
    <>
      {/* Solar Panel - Top Left */}
      <group ref={solarRef} position={[-2.5, 0.5, 2.5]}>
        {/* Panel surface */}
        <mesh rotation={[-Math.PI / 6, 0, 0]}>
          <boxGeometry args={[0.8, 0.05, 0.6]} />
          <meshStandardMaterial 
            color="#1E3A8A"
            emissive="#FDB022"
            emissiveIntensity={activeSource === 'solar' ? 0.6 : 0.1}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        {/* Panel stand */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 0.6]} />
          <meshStandardMaterial color="#374151" />
        </mesh>
        {/* Light indicator */}
        {activeSource === 'solar' && (
          <pointLight position={[0, 0.3, 0]} color="#FDB022" intensity={1} distance={3} />
        )}
      </group>

      {/* Battery - Top Right */}
      <group ref={batteryRef} position={[2.5, -0.5, 2.5]}>
        {/* Battery body */}
        <mesh>
          <cylinderGeometry args={[0.3, 0.3, 0.8]} />
          <meshStandardMaterial 
            color="#1F2937"
            emissive="#FF6B35"
            emissiveIntensity={activeSource === 'battery' ? 0.6 : 0.1}
            metalness={0.6}
            roughness={0.3}
          />
        </mesh>
        {/* Battery terminal */}
        <mesh position={[0, 0.5, 0]}>
          <cylinderGeometry args={[0.1, 0.1, 0.2]} />
          <meshStandardMaterial 
            color="#6B7280"
            emissive="#FF6B35"
            emissiveIntensity={activeSource === 'battery' ? 0.8 : 0.1}
          />
        </mesh>
        {/* Light indicator */}
        {activeSource === 'battery' && (
          <pointLight position={[0, 0.5, 0]} color="#FF6B35" intensity={1} distance={3} />
        )}
      </group>

      {/* Grid/Utility Pole - Back */}
      <group ref={gridRef} position={[0, 0, -2.8]}>
        {/* Pole */}
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 2]} />
          <meshStandardMaterial 
            color="#4B5563"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.4 : 0.05}
          />
        </mesh>
        {/* Cross beam */}
        <mesh position={[0, 0.8, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.05, 0.05, 1.2]} />
          <meshStandardMaterial 
            color="#374151"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.5 : 0.05}
          />
        </mesh>
        {/* Power lines */}
        <mesh position={[-0.4, 0.8, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 0.5]} />
          <meshStandardMaterial 
            color="#1F2937"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.7 : 0.1}
          />
        </mesh>
        <mesh position={[0.4, 0.8, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 0.5]} />
          <meshStandardMaterial 
            color="#1F2937"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.7 : 0.1}
          />
        </mesh>
        {/* Light indicator */}
        {activeSource === 'grid' && (
          <pointLight position={[0, 1, 0]} color="#EF4444" intensity={1.2} distance={4} />
        )}
      </group>
    </>
  )
}

export default function DigitalTwin({ 
  lightIntensity, 
  activeSource, 
  brightnessThreshold,
  weatherCondition = 'sunny',
  className 
}: DigitalTwinProps) {
  return (
    <div className={className} style={{ width: '100%', height: '100%' }}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[4, 2, 4]} />
        <OrbitControls 
          enableZoom={true}
          enablePan={true}
          minDistance={3}
          maxDistance={15}
          autoRotate
          autoRotateSpeed={0.5}
        />
        <Room 
          lightIntensity={lightIntensity} 
          activeSource={activeSource}
          brightnessThreshold={brightnessThreshold}
          weatherCondition={weatherCondition}
        />
      </Canvas>
    </div>
  )
}
