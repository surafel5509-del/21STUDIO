package com.twentyone.engine.physics

import com.twentyone.engine.ecs.Component
import com.twentyone.engine.ecs.Entity
import com.twentyone.engine.ecs.GameSystem
import com.twentyone.engine.ecs.World
import com.twentyone.engine.math.Vec2
import kotlin.math.floor
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt

/** Axis-aligned box represented by center and half extents. */
data class Aabb(val center: Vec2, val half: Vec2) {
    fun overlaps(other: Aabb): Boolean =
        kotlin.math.abs(center.x - other.center.x) <= half.x + other.half.x &&
            kotlin.math.abs(center.y - other.center.y) <= half.y + other.half.y
}

data class Circle(val center: Vec2, val radius: Float)

data class Transform2D(val position: Vec2 = Vec2(), var rotationDegrees: Float = 0f) : Component

data class Rigidbody(
    val velocity: Vec2 = Vec2(),
    val acceleration: Vec2 = Vec2(),
    var inverseMass: Float = 1f,
    var linearDamping: Float = 0f,
    var restitution: Float = 0f,
    var isStatic: Boolean = false,
) : Component

sealed interface ColliderShape {
    data class Box(val halfExtents: Vec2) : ColliderShape
    data class Disk(val radius: Float) : ColliderShape
}

data class Collider(
    val shape: ColliderShape,
    var trigger: Boolean = false,
    var layer: Int = 1,
    var mask: Int = -1,
) : Component

data class Collision(val first: Entity, val second: Entity, val normal: Vec2, val penetration: Float, val trigger: Boolean)
data class RaycastHit(val entity: Entity, val point: Vec2, val normal: Vec2, val distance: Float)

/** Real-time impulse solver for AABB and circle colliders. */
class PhysicsSystem(
    private val gravity: Vec2 = Vec2(0f, -18f),
    private val onCollision: (Collision) -> Unit = {},
) : GameSystem {
    override fun update(world: World, deltaSeconds: Float) {
        val entities = world.query<Transform2D, Rigidbody>()
        entities.forEach { entity ->
            val transform = world.get<Transform2D>(entity) ?: return@forEach
            val body = world.get<Rigidbody>(entity) ?: return@forEach
            if (body.isStatic) return@forEach
            body.velocity.add((gravity.x + body.acceleration.x) * deltaSeconds, (gravity.y + body.acceleration.y) * deltaSeconds)
            val damping = (1f - body.linearDamping * deltaSeconds).coerceIn(0f, 1f)
            body.velocity.scale(damping)
            transform.position.add(body.velocity.x * deltaSeconds, body.velocity.y * deltaSeconds)
        }
        val collidable = world.query<Transform2D, Collider>()
        for (i in collidable.indices) for (j in i + 1 until collidable.size) {
            val first = collidable[i]; val second = collidable[j]
            val a = world.get<Collider>(first) ?: continue; val b = world.get<Collider>(second) ?: continue
            if ((a.mask and b.layer) == 0 || (b.mask and a.layer) == 0) continue
            val contact = contact(world.get<Transform2D>(first)!!, a, world.get<Transform2D>(second)!!, b) ?: continue
            val trigger = a.trigger || b.trigger
            onCollision(Collision(first, second, contact.normal, contact.penetration, trigger))
            if (!trigger) resolve(world, first, second, contact)
        }
    }

    fun raycast(world: World, origin: Vec2, direction: Vec2, maxDistance: Float): RaycastHit? {
        val length = sqrt(direction.lengthSquared()); if (length == 0f) return null
        val dir = Vec2(direction.x / length, direction.y / length)
        return world.query<Transform2D, Collider>().mapNotNull { entity ->
            val transform = world.get<Transform2D>(entity)!!; val collider = world.get<Collider>(entity)!!
            rayShape(entity, origin, dir, maxDistance, transform, collider)
        }.minByOrNull(RaycastHit::distance)
    }

    private data class Contact(val normal: Vec2, val penetration: Float)
    private fun contact(aT: Transform2D, a: Collider, bT: Transform2D, b: Collider): Contact? = when {
        a.shape is ColliderShape.Box && b.shape is ColliderShape.Box -> boxBox(aT.position, a.shape, bT.position, b.shape)
        a.shape is ColliderShape.Disk && b.shape is ColliderShape.Disk -> diskDisk(aT.position, a.shape, bT.position, b.shape)
        a.shape is ColliderShape.Box && b.shape is ColliderShape.Disk -> boxDisk(aT.position, a.shape, bT.position, b.shape)
        else -> boxDisk(bT.position, b.shape as ColliderShape.Box, aT.position, a.shape as ColliderShape.Disk)?.let { Contact(Vec2(-it.normal.x, -it.normal.y), it.penetration) }
    }
    private fun boxBox(a: Vec2, ah: ColliderShape.Box, b: Vec2, bh: ColliderShape.Box): Contact? {
        val dx = b.x - a.x; val px = ah.halfExtents.x + bh.halfExtents.x - kotlin.math.abs(dx); if (px <= 0f) return null
        val dy = b.y - a.y; val py = ah.halfExtents.y + bh.halfExtents.y - kotlin.math.abs(dy); if (py <= 0f) return null
        return if (px < py) Contact(Vec2(if (dx < 0f) -1f else 1f, 0f), px) else Contact(Vec2(0f, if (dy < 0f) -1f else 1f), py)
    }
    private fun diskDisk(a: Vec2, ar: ColliderShape.Disk, b: Vec2, br: ColliderShape.Disk): Contact? { val dx = b.x-a.x; val dy = b.y-a.y; val distance = sqrt(dx*dx+dy*dy); val sum = ar.radius+br.radius; if (distance >= sum) return null; return Contact(if (distance == 0f) Vec2(1f,0f) else Vec2(dx/distance,dy/distance), sum-distance) }
    private fun boxDisk(box: Vec2, shape: ColliderShape.Box, disk: Vec2, circle: ColliderShape.Disk): Contact? { val closestX = disk.x.coerceIn(box.x-shape.halfExtents.x, box.x+shape.halfExtents.x); val closestY = disk.y.coerceIn(box.y-shape.halfExtents.y, box.y+shape.halfExtents.y); return diskDisk(Vec2(closestX,closestY), ColliderShape.Disk(0f), disk, circle) }
    private fun resolve(world: World, first: Entity, second: Entity, contact: Contact) { val a = world.get<Rigidbody>(first) ?: return; val b = world.get<Rigidbody>(second) ?: return; val invA = if (a.isStatic) 0f else a.inverseMass; val invB = if (b.isStatic) 0f else b.inverseMass; val total = invA+invB; if (total == 0f) return; val correction = contact.penetration / total; world.get<Transform2D>(first)?.position?.add(-contact.normal.x*correction*invA, -contact.normal.y*correction*invA); world.get<Transform2D>(second)?.position?.add(contact.normal.x*correction*invB, contact.normal.y*correction*invB); val relative = (b.velocity.x-a.velocity.x)*contact.normal.x+(b.velocity.y-a.velocity.y)*contact.normal.y; if (relative > 0f) return; val impulse = -(1f+min(a.restitution,b.restitution))*relative/total; a.velocity.add(-contact.normal.x*impulse*invA,-contact.normal.y*impulse*invA); b.velocity.add(contact.normal.x*impulse*invB,contact.normal.y*impulse*invB) }
    private fun rayShape(entity: Entity, origin: Vec2, dir: Vec2, maxDistance: Float, transform: Transform2D, collider: Collider): RaycastHit? {
        val distance = when (val shape = collider.shape) {
            is ColliderShape.Disk -> { val offset = Vec2(origin.x-transform.position.x, origin.y-transform.position.y); val b = offset.dot(dir); val c = offset.lengthSquared()-shape.radius*shape.radius; val discriminant = b*b-c; if (discriminant < 0f) null else -b-sqrt(discriminant) }
            is ColliderShape.Box -> { val minX=transform.position.x-shape.halfExtents.x; val maxX=transform.position.x+shape.halfExtents.x; val minY=transform.position.y-shape.halfExtents.y; val maxY=transform.position.y+shape.halfExtents.y; val tx1=(minX-origin.x)/dir.x; val tx2=(maxX-origin.x)/dir.x; val ty1=(minY-origin.y)/dir.y; val ty2=(maxY-origin.y)/dir.y; val enter=max(min(tx1,tx2),min(ty1,ty2)); val exit=min(max(tx1,tx2),max(ty1,ty2)); if (exit < max(enter,0f)) null else enter }
        }?.takeIf { it in 0f..maxDistance } ?: return null
        val point = Vec2(origin.x+dir.x*distance, origin.y+dir.y*distance)
        val normal = when (collider.shape) { is ColliderShape.Disk -> Vec2((point.x-transform.position.x)/(collider.shape as ColliderShape.Disk).radius, (point.y-transform.position.y)/(collider.shape as ColliderShape.Disk).radius); is ColliderShape.Box -> Vec2() }
        return RaycastHit(entity, point, normal, distance)
    }
}

/** Uniform-grid broad phase. `floor` makes negative coordinates behave correctly. */
class SpatialHash(private val cellSize: Float) {
    private val cells = mutableMapOf<Long, MutableSet<Entity>>()
    init { require(cellSize > 0f) }
    fun clear() = cells.clear()
    fun insert(entity: Entity, bounds: Aabb) { forEachCell(bounds) { cells.getOrPut(it) { linkedSetOf() }.add(entity) } }
    fun candidates(bounds: Aabb): Set<Entity> = buildSet { forEachCell(bounds) { cells[it]?.let(::addAll) } }
    private fun forEachCell(bounds: Aabb, action: (Long) -> Unit) { val minX=floor((bounds.center.x-bounds.half.x)/cellSize).toInt(); val maxX=floor((bounds.center.x+bounds.half.x)/cellSize).toInt(); val minY=floor((bounds.center.y-bounds.half.y)/cellSize).toInt(); val maxY=floor((bounds.center.y+bounds.half.y)/cellSize).toInt(); for (x in minX..maxX) for(y in minY..maxY) action((x.toLong() shl 32) xor (y.toLong() and 0xffffffffL)) }
}
