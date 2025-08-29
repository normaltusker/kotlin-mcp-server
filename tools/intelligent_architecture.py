#!/usr/bin/env python3
"""
Intelligent Architecture Tools for Room database setup.

Provides a functional implementation for setting up a Room database with
entities, DAOs, a database class, migration handling and optional SQLCipher
encryption. The tool also updates Gradle dependencies when possible.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentRoomDatabaseTool(IntelligentToolBase):
    """Create Room database infrastructure with intelligent features."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Generate Room entities, DAOs, database class and update Gradle."""

        database_name = arguments.get("database_name", "AppDatabase")
        package_name = arguments.get("package_name", "com.example.app")
        entities_arg = arguments.get("entities", [])
        version = int(arguments.get("version", 1))
        use_encryption = bool(arguments.get("use_encryption", False))
        include_migration = bool(arguments.get("include_migration", False))

        # Normalize entity definitions
        entities: List[Dict[str, Any]] = []
        for item in entities_arg:
            if isinstance(item, str):
                # Provide a simple default structure
                entities.append(
                    {
                        "name": item,
                        "fields": [
                            {"name": "id", "type": "Int", "primary_key": True},
                            {"name": "name", "type": "String"},
                        ],
                    }
                )
            elif isinstance(item, dict):
                entities.append(item)

        package_path = package_name.replace(".", "/")
        base_path = (
            self.project_path
            / "src"
            / "main"
            / "kotlin"
            / package_path
            / "data"
        )
        entity_dir = base_path / "entity"
        dao_dir = base_path / "dao"
        entity_dir.mkdir(parents=True, exist_ok=True)
        dao_dir.mkdir(parents=True, exist_ok=True)

        created_files: List[str] = []
        entity_names: List[str] = []

        # Generate entities and DAOs
        for entity in entities:
            name = entity["name"]
            fields = entity.get("fields", [])
            entity_code = self._generate_entity_code(package_name, name, fields)
            entity_file = entity_dir / f"{name}.kt"
            entity_file.write_text(entity_code, encoding="utf-8")
            created_files.append(str(entity_file))
            entity_names.append(name)

            dao_code = self._generate_dao_code(package_name, name)
            dao_file = dao_dir / f"{name}Dao.kt"
            dao_file.write_text(dao_code, encoding="utf-8")
            created_files.append(str(dao_file))

        # Generate database class
        db_code = self._generate_database_code(
            package_name,
            database_name,
            entity_names,
            version,
            include_migration,
            use_encryption,
        )
        db_file = base_path / f"{database_name}.kt"
        db_file.write_text(db_code, encoding="utf-8")
        created_files.append(str(db_file))

        # Update Gradle dependencies
        dependencies_added = self._update_gradle_dependencies(use_encryption)

        return {
            "database": database_name,
            "entities": entity_names,
            "version": version,
            "files_created": created_files,
            "dependencies_added": dependencies_added,
            "encryption_enabled": use_encryption,
        }

    # ------------------------------------------------------------------
    # Code generation helpers
    # ------------------------------------------------------------------
    def _generate_entity_code(
        self, package_name: str, entity_name: str, fields: List[Dict[str, Any]]
    ) -> str:
        """Generate Kotlin code for a Room entity."""

        field_lines: List[str] = []
        for field in fields:
            prefix = "@PrimaryKey\n    " if field.get("primary_key") else ""
            line = f"{prefix}val {field['name']}: {field['type']}"
            if field.get("nullable"):
                line += "?"
            if field.get("default") is not None:
                line += f" = {field['default']}"
            field_lines.append(line)

        if not field_lines:
            field_lines = ["@PrimaryKey\n    val id: Int = 0"]

        fields_code = ",\n    ".join(field_lines)

        return f"""package {package_name}.data.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity
data class {entity_name}(
    {fields_code}
)
"""

    def _generate_dao_code(self, package_name: str, entity_name: str) -> str:
        """Generate Kotlin code for a DAO interface."""

        return f"""package {package_name}.data.dao

import androidx.room.*
import kotlinx.coroutines.flow.Flow
import {package_name}.data.entity.{entity_name}

@Dao
interface {entity_name}Dao {{
    @Query("SELECT * FROM {entity_name}")
    fun getAll(): Flow<List<{entity_name}>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: {entity_name})

    @Delete
    suspend fun delete(item: {entity_name})
}}
"""

    def _generate_database_code(
        self,
        package_name: str,
        database_name: str,
        entities: List[str],
        version: int,
        include_migration: bool,
        use_encryption: bool,
    ) -> str:
        """Generate Kotlin code for the Room database class."""

        imports = [
            "import android.content.Context",
            "import androidx.room.Database",
            "import androidx.room.Room",
            "import androidx.room.RoomDatabase",
            f"import {package_name}.data.dao.*",
            f"import {package_name}.data.entity.*",
        ]
        if include_migration and version > 1:
            imports.extend(
                [
                    "import androidx.room.migration.Migration",
                    "import androidx.sqlite.db.SupportSQLiteDatabase",
                ]
            )
        if use_encryption:
            imports.extend(
                [
                    "import net.sqlcipher.database.SupportFactory",
                    "import net.sqlcipher.database.SQLiteDatabase",
                ]
            )

        imports_code = "\n".join(imports)
        entity_list = ", ".join(f"{e}::class" for e in entities)

        dao_methods = "".join(
            f"    abstract fun {e[0].lower() + e[1:]}Dao(): {e}Dao\n" for e in entities
        )

        migration_usage = (
            "            builder.addMigrations(MIGRATION_{version-1}_{version})\n"
            if include_migration and version > 1
            else ""
        )

        encryption_usage = (
            "            if (useEncryption && password != null) {\n"
            "                val passphrase = SQLiteDatabase.getBytes(password)\n"
            "                val factory = SupportFactory(passphrase)\n"
            "                builder.openHelperFactory(factory)\n"
            "            }\n"
            if use_encryption
            else ""
        )

        migration_code = (
            f"""\nval MIGRATION_{version-1}_{version} = object : Migration({version-1}, {version}) {{
    override fun migrate(database: SupportSQLiteDatabase) {{
        // TODO: Implement migration logic
    }}
}}
"""
            if include_migration and version > 1
            else ""
        )

        return f"""package {package_name}.data

{imports_code}

@Database(entities = [{entity_list}], version = {version})
abstract class {database_name} : RoomDatabase() {{
{dao_methods}
    companion object {{
        @Volatile private var INSTANCE: {database_name}? = null

        fun getInstance(
            context: Context,
            useEncryption: Boolean = {str(use_encryption).lower()},
            password: CharArray? = null
        ): {database_name} {{
            return INSTANCE ?: synchronized(this) {{
                val builder = Room.databaseBuilder(
                    context.applicationContext,
                    {database_name}::class.java,
                    "{database_name.lower()}"
                )
{encryption_usage}{migration_usage}                val db = builder.build()
                INSTANCE = db
                db
            }}
        }}
    }}
}}
{migration_code}
"""

    # ------------------------------------------------------------------
    # Gradle dependency management
    # ------------------------------------------------------------------
    def _update_gradle_dependencies(self, use_encryption: bool) -> List[str]:
        """Add required dependencies to Gradle build file if possible."""

        deps = [
            'implementation("androidx.room:room-runtime:2.6.1")',
            'kapt("androidx.room:room-compiler:2.6.1")',
            'implementation("androidx.room:room-ktx:2.6.1")',
        ]
        if use_encryption:
            deps.append('implementation("net.zetetic:android-database-sqlcipher:4.5.4")')

        build_file: Optional[Path] = None
        for candidate in ["build.gradle.kts", "build.gradle"]:
            candidate_path = self.project_path / candidate
            if candidate_path.exists():
                build_file = candidate_path
                break

        if build_file is None:
            # No build file found - return suggestions
            return deps

        content = build_file.read_text(encoding="utf-8")
        added: List[str] = []
        for dep in deps:
            if dep not in content:
                added.append(dep)

        if added:
            if "dependencies {" in content:
                updated = content.replace(
                    "dependencies {",
                    "dependencies {\n    " + "\n    ".join(added) + "\n",
                )
            else:
                updated = (
                    content
                    + "\n\ndependencies {\n    "
                    + "\n    ".join(added)
                    + "\n}\n"
                )
            build_file.write_text(updated, encoding="utf-8")

        return added
