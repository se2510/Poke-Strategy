"""Pokemon business logic service."""

from typing import Any, Dict, List
from collections import defaultdict

from core.interfaces import IPokemonRepository, IPokemonService
from core.exceptions import ValidationError


class PokemonService(IPokemonService):
    """Service implementing pokemon business logic with injected dependencies."""
    
    def __init__(self, pokemon_repository: IPokemonRepository):
        self._repository = pokemon_repository
    
    async def get_pokemon_info(self, name: str) -> Dict[str, Any]:
        """Get enriched pokemon information.
        
        Args:
            name: Pokemon name
            
        Returns:
            Processed pokemon data
            
        Raises:
            ValidationError: If name is empty
        """
        if not name or not name.strip():
            raise ValidationError(
                message="Pokemon name cannot be empty",
                field="name",
                value=name
            )
        
        return await self._repository.get_pokemon(name)
    
    async def search_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search pokemons with pagination.
        
        Args:
            limit: Maximum number of results
            offset: Starting index for pagination
            
        Returns:
            Paginated pokemon list
            
        Raises:
            ValidationError: If parameters are invalid
        """
        if limit < 1 or limit > 100:
            raise ValidationError(
                message="Limit must be between 1 and 100",
                field="limit",
                value=limit
            )
        
        if offset < 0:
            raise ValidationError(
                message="Offset cannot be negative",
                field="offset",
                value=offset
            )
        
        return await self._repository.list_pokemons(limit=limit, offset=offset)
    
    async def get_pokemon_with_abilities(self, name: str) -> Dict[str, Any]:
        """Get pokemon with detailed ability information."""
        pokemon = await self._repository.get_pokemon(name)
        
        abilities_details = []
        if "abilities" in pokemon:
            for ability_entry in pokemon["abilities"][:3]:
                ability_name = ability_entry.get("ability", {}).get("name")
                if ability_name:
                    try:
                        ability_data = await self._repository.get_ability(ability_name)
                        abilities_details.append(ability_data)
                    except Exception:
                        pass
        
        return {
            **pokemon,
            "abilities_details": abilities_details
        }

    async def get_pokemon_summary(self, name: str) -> Dict[str, Any]:
        """Return a compact summary of a Pokémon for limited context agents.

        Reduces the large PokeAPI payload to essential, high-signal fields.

        Included keys:
        - id, name, height, weight, base_experience
        - types: [str]
        - abilities: [str] (máx 3)
        - stats: { stat_name: base_stat }
        - moves_sample: primeros N movimientos (máx 10)
        - moves_count: total de movimientos en dataset original
        - sprite: url principal (front_default si disponible)
        - is_default: bandera original
        - forms: nombres de formas (máx 5)
        - order: orden interno

        Args:
            name: Nombre del Pokémon.
        Returns:
            Diccionario reducido listo para consumo por un LLM.
        Raises:
            ValidationError: si name está vacío.
        """
        if not name or not name.strip():
            raise ValidationError(
                message="Pokemon name cannot be empty",
                field="name",
                value=name
            )

        raw = await self._repository.get_pokemon(name)

        # Extraer listas controladas con salvaguardas.
        types = [t.get("type", {}).get("name") for t in raw.get("types", []) if isinstance(t, dict)]
        abilities = [a.get("ability", {}).get("name") for a in raw.get("abilities", []) if isinstance(a, dict)]
        abilities = [a for a in abilities if a][:3]  # limitar

        stats_pairs = {}
        for s in raw.get("stats", []):
            if isinstance(s, dict):
                stat_name = s.get("stat", {}).get("name")
                base = s.get("base_stat")
                if stat_name and isinstance(base, (int, float)):
                    stats_pairs[stat_name] = base

        moves = []
        for m in raw.get("moves", [])[:10]:  # sample primeros 10
            if isinstance(m, dict):
                mv_name = m.get("move", {}).get("name")
                if mv_name:
                    moves.append(mv_name)

        forms = []
        for f in raw.get("forms", [])[:5]:
            if isinstance(f, dict):
                fname = f.get("name")
                if fname:
                    forms.append(fname)

        sprite = None
        sprites = raw.get("sprites", {})
        if isinstance(sprites, dict):
            # prefer front_default; fallback a otros candidatos
            sprite = sprites.get("front_default") or sprites.get("other", {}).get("official-artwork", {}).get("front_default")

        summary: Dict[str, Any] = {
            "id": raw.get("id"),
            "name": raw.get("name"),
            "types": types,
            "abilities": abilities,
            "height": raw.get("height"),
            "weight": raw.get("weight"),
            "base_experience": raw.get("base_experience"),
            "stats": stats_pairs,
            "moves_sample": moves,
            "moves_count": len(raw.get("moves", [])),
            "sprite": sprite,
            "is_default": raw.get("is_default"),
            "forms": forms,
            "order": raw.get("order"),
        }

        # Eliminar claves con valor None para compactar aún más.
        compact = {k: v for k, v in summary.items() if v is not None}
        return compact

    async def get_type_summary(self, type_name: str, limit: int = 10) -> Dict[str, Any]:
        if not type_name or not type_name.strip():
            raise ValidationError(
                message="Type name cannot be empty",
                field="type_name",
                value=type_name
            )
        if limit < 1 or limit > 50:
            raise ValidationError(
                message="Limit must be between 1 and 50",
                field="limit",
                value=limit
            )
        type_data = await self._repository.get_type(type_name)
        pokes_raw = type_data.get("pokemon", [])
        summaries: list[Dict[str, Any]] = []
        for entry in pokes_raw[:limit]:
            name = entry.get("pokemon", {}).get("name") if isinstance(entry, dict) else None
            if name:
                try:
                    summaries.append(await self.get_pokemon_summary(name))
                except Exception:
                    pass
        return {
            "type": type_name.lower(),
            "total_available": len(pokes_raw),
            "returned": len(summaries),
            "pokemons": summaries,
        }

    async def compare_pokemons(self, first: str, second: str) -> Dict[str, Any]:
        if not first or not second:
            raise ValidationError(
                message="Both pokemon names are required",
                field="names",
                value=f"{first}, {second}"
            )
        p1 = await self.get_pokemon_summary(first)
        p2 = await self.get_pokemon_summary(second)
        def diff_stat(stat: str):
            s1 = p1.get("stats", {}).get(stat)
            s2 = p2.get("stats", {}).get(stat)
            if isinstance(s1, (int, float)) and isinstance(s2, (int, float)):
                if s1 > s2:
                    return first
                if s2 > s1:
                    return second
            return None
        comparison = {
            "higher_attack": diff_stat("attack"),
            "higher_defense": diff_stat("defense"),
            "higher_hp": diff_stat("hp"),
            "types_overlap": sorted(set(p1.get("types", [])) & set(p2.get("types", []))),
        }
        return {"first": p1, "second": p2, "comparison": comparison}

    async def group_pokemons_by_type(self, pokemon_names: List[str]) -> Dict[str, Any]:
        """Group Pokémon by their primary type.
        
        Args:
            pokemon_names: List of Pokémon names to group
            
        Returns:
            Dictionary with type groups and a markdown table
            
        Raises:
            ValidationError: If pokemon_names is empty
        """
        if not pokemon_names:
            raise ValidationError(
                message="Pokemon names list cannot be empty",
                field="pokemon_names",
                value=[]
            )
        
        groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        summaries = []
        
        for name in pokemon_names:
            try:
                summary = await self.get_pokemon_summary(name)
                summaries.append(summary)
                types = summary.get("types", [])
                primary_type = types[0] if types else "unknown"
                groups[primary_type].append(summary)
            except Exception:
                continue
        
        # Generate markdown table
        markdown_lines = ["# Pokémon Grouped by Primary Type\n"]
        for type_name, pokemon_list in sorted(groups.items()):
            markdown_lines.append(f"\n## {type_name.capitalize()} Type ({len(pokemon_list)} Pokémon)\n")
            markdown_lines.append("| Name | Types | HP | Attack | Defense | Total Stats |")
            markdown_lines.append("|------|-------|----|---------|------------|-------------|")
            
            for poke in pokemon_list:
                name = poke.get("name", "unknown")
                types_str = "/".join(poke.get("types", []))
                stats = poke.get("stats", {})
                hp = stats.get("hp", 0)
                attack = stats.get("attack", 0)
                defense = stats.get("defense", 0)
                total = sum(stats.values()) if isinstance(stats, dict) else 0
                
                markdown_lines.append(
                    f"| {name} | {types_str} | {hp} | {attack} | {defense} | {total} |"
                )
        
        markdown_table = "\n".join(markdown_lines)
        
        return {
            "groups": {k: [p.get("name") for p in v] for k, v in groups.items()},
            "summaries": summaries,
            "markdown": markdown_table,
            "total_pokemons": len(summaries),
            "type_count": len(groups)
        }

    async def classify_by_role(self, pokemon_names: List[str]) -> Dict[str, Any]:
        """Classify Pokémon by battle role based on stats.
        
        Roles:
        - Tank: High HP and Defense
        - Attacker: High Attack or Special Attack
        - Balanced: Relatively even stats
        - Fast: High Speed
        
        Args:
            pokemon_names: List of Pokémon names to classify
            
        Returns:
            Dictionary with role classifications and markdown table
        """
        if not pokemon_names:
            raise ValidationError(
                message="Pokemon names list cannot be empty",
                field="pokemon_names",
                value=[]
            )
        
        roles: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        for name in pokemon_names:
            try:
                summary = await self.get_pokemon_summary(name)
                stats = summary.get("stats", {})
                
                hp = stats.get("hp", 0)
                attack = stats.get("attack", 0)
                defense = stats.get("defense", 0)
                sp_attack = stats.get("special-attack", 0)
                sp_defense = stats.get("special-defense", 0)
                speed = stats.get("speed", 0)
                
                # Classify by role (prioritize attacker, then speed, then tank, then balanced)
                if attack >= 100 or sp_attack >= 100:
                    role = "attacker"
                elif speed >= 100:
                    role = "fast"
                elif (hp >= 80 and defense >= 80) or (hp >= 200):  # Tank: high HP+Def OR extreme HP
                    role = "tank"
                else:
                    role = "balanced"
                
                roles[role].append(summary)
            except Exception:
                continue
        
        # Generate markdown table
        markdown_lines = ["# Pokémon Classification by Battle Role\n"]
        
        role_descriptions = {
            "tank": "High HP and Defense - absorbs damage",
            "attacker": "High Attack/Special Attack - deals heavy damage",
            "fast": "High Speed - strikes first",
            "balanced": "Well-rounded stats"
        }
        
        for role_name, pokemon_list in sorted(roles.items()):
            desc = role_descriptions.get(role_name, "")
            markdown_lines.append(f"\n## {role_name.capitalize()} ({len(pokemon_list)} Pokémon)")
            markdown_lines.append(f"*{desc}*\n")
            markdown_lines.append("| Name | Types | HP | Atk | Def | Sp.Atk | Sp.Def | Speed |")
            markdown_lines.append("|------|-------|----|----|-----|--------|--------|-------|")
            
            for poke in pokemon_list:
                name = poke.get("name", "unknown")
                types_str = "/".join(poke.get("types", []))
                stats = poke.get("stats", {})
                
                markdown_lines.append(
                    f"| {name} | {types_str} | {stats.get('hp', 0)} | "
                    f"{stats.get('attack', 0)} | {stats.get('defense', 0)} | "
                    f"{stats.get('special-attack', 0)} | {stats.get('special-defense', 0)} | "
                    f"{stats.get('speed', 0)} |"
                )
        
        return {
            "roles": {k: [p.get("name") for p in v] for k, v in roles.items()},
            "markdown": "\n".join(markdown_lines),
            "total_classified": sum(len(v) for v in roles.values())
        }

    async def calculate_team_strength(self, pokemon_names: List[str]) -> Dict[str, Any]:
        """Calculate team strength and synergies.
        
        Analyzes:
        - Total stats
        - Type coverage
        - Type weaknesses
        - Role distribution
        
        Args:
            pokemon_names: List of Pokémon names (max 6 for standard team)
            
        Returns:
            Team analysis with strengths, weaknesses, and recommendations
        """
        if not pokemon_names:
            raise ValidationError(
                message="Pokemon names list cannot be empty",
                field="pokemon_names",
                value=[]
            )
        
        if len(pokemon_names) > 6:
            raise ValidationError(
                message="Team size cannot exceed 6 Pokemon",
                field="pokemon_names",
                value=len(pokemon_names)
            )
        
        team = []
        all_types = []
        total_stats = defaultdict(int)
        roles = defaultdict(int)
        
        for name in pokemon_names:
            try:
                summary = await self.get_pokemon_summary(name)
                team.append(summary)
                
                # Collect types
                all_types.extend(summary.get("types", []))
                
                # Sum stats
                stats = summary.get("stats", {})
                for stat_name, value in stats.items():
                    if isinstance(value, (int, float)):
                        total_stats[stat_name] += value
                
                # Classify role
                hp = stats.get("hp", 0)
                attack = stats.get("attack", 0)
                defense = stats.get("defense", 0)
                sp_attack = stats.get("special-attack", 0)
                speed = stats.get("speed", 0)
                
                # Classify role (prioritize attacker, then speed, then tank, then balanced)
                if attack >= 100 or sp_attack >= 100:
                    roles["attacker"] += 1
                elif speed >= 100:
                    roles["fast"] += 1
                elif (hp >= 80 and defense >= 80) or (hp >= 200):  # Tank: high HP+Def OR extreme HP
                    roles["tank"] += 1
                else:
                    roles["balanced"] += 1
                    
            except Exception:
                continue
        
        # Calculate type coverage
        unique_types = set(all_types)
        type_distribution = {t: all_types.count(t) for t in unique_types}
        
        # Average stats
        team_size = len(team)
        avg_stats = {k: round(v / team_size, 2) if team_size > 0 else 0 
                     for k, v in total_stats.items()}
        
        # Generate explanation
        explanation_lines = []
        explanation_lines.append(f"## Team Analysis ({team_size} Pokémon)\n")
        
        explanation_lines.append("### Type Coverage")
        explanation_lines.append(f"- **Unique Types**: {len(unique_types)} ({', '.join(sorted(unique_types))})")
        explanation_lines.append(f"- **Type Distribution**: {dict(sorted(type_distribution.items()))}\n")
        
        explanation_lines.append("### Average Team Stats")
        for stat, value in sorted(avg_stats.items()):
            explanation_lines.append(f"- **{stat.replace('-', ' ').title()}**: {value}")
        
        explanation_lines.append("\n### Role Distribution")
        for role, count in sorted(roles.items()):
            explanation_lines.append(f"- **{role.capitalize()}**: {count}")
        
        explanation_lines.append("\n### Strengths")
        strengths = []
        if len(unique_types) >= 5:
            strengths.append("Excellent type diversity for coverage")
        if avg_stats.get("attack", 0) >= 90 or avg_stats.get("special-attack", 0) >= 90:
            strengths.append("High offensive potential")
        if avg_stats.get("defense", 0) >= 80 and avg_stats.get("hp", 0) >= 70:
            strengths.append("Strong defensive capabilities")
        if roles.get("balanced", 0) >= 2:
            strengths.append("Versatile team composition")
        
        for s in strengths if strengths else ["Balanced team"]:
            explanation_lines.append(f"- {s}")
        
        explanation_lines.append("\n### Recommendations")
        recommendations = []
        if len(unique_types) < 4:
            recommendations.append("Consider adding more type diversity")
        if roles.get("tank", 0) == 0:
            recommendations.append("Team lacks defensive tanks")
        if roles.get("attacker", 0) == 0:
            recommendations.append("Team needs more offensive power")
        if avg_stats.get("speed", 0) < 60:
            recommendations.append("Consider adding faster Pokémon")
        
        for r in recommendations if recommendations else ["Team is well-balanced"]:
            explanation_lines.append(f"- {r}")
        
        return {
            "team": [p.get("name") for p in team],
            "team_size": team_size,
            "type_coverage": list(unique_types),
            "type_distribution": type_distribution,
            "average_stats": avg_stats,
            "role_distribution": dict(roles),
            "explanation": "\n".join(explanation_lines),
            "strengths": strengths,
            "recommendations": recommendations
        }

    async def recommend_team_for_battle(
        self, 
        available_pokemon: List[str], 
        opponent_types: List[str] | None = None,
        team_size: int = 6
    ) -> Dict[str, Any]:
        """Recommend optimal team composition for battle.
        
        Args:
            available_pokemon: List of available Pokémon names
            opponent_types: Expected opponent type(s) to counter (optional)
            team_size: Number of Pokémon to select (default 6)
            
        Returns:
            Recommended team with justification
        """
        if not available_pokemon:
            raise ValidationError(
                message="Available pokemon list cannot be empty",
                field="available_pokemon",
                value=[]
            )
        
        if team_size < 1 or team_size > 6:
            raise ValidationError(
                message="Team size must be between 1 and 6",
                field="team_size",
                value=team_size
            )
        
        # Fetch all summaries
        candidates = []
        for name in available_pokemon[:50]:  # Limit to prevent excessive API calls
            try:
                summary = await self.get_pokemon_summary(name)
                candidates.append(summary)
            except Exception:
                continue
        
        # Score each Pokémon
        scored_candidates = []
        for poke in candidates:
            stats = poke.get("stats", {})
            total_stats = sum(stats.values()) if isinstance(stats, dict) else 0
            
            # Base score from total stats
            score = total_stats
            
            # Bonus for type advantage against opponents
            if opponent_types:
                poke_types = poke.get("types", [])
                # Simple heuristic: boost score if not sharing types with opponent
                if not any(t in opponent_types for t in poke_types):
                    score += 50
            
            # Bonus for versatility (multiple types)
            if len(poke.get("types", [])) >= 2:
                score += 20
            
            scored_candidates.append({"pokemon": poke, "score": score})
        
        # Select top N
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        selected = scored_candidates[:team_size]
        
        team_names = [s["pokemon"].get("name") for s in selected]
        
        # Generate justification
        justification_lines = [f"## Recommended Team ({len(team_names)} Pokémon)\n"]
        
        if opponent_types:
            justification_lines.append(f"**Target**: Counter {', '.join(opponent_types)} types\n")
        
        justification_lines.append("### Selected Pokémon")
        for i, item in enumerate(selected, 1):
            poke = item["pokemon"]
            name = poke.get("name", "unknown")
            types = "/".join(poke.get("types", []))
            stats = poke.get("stats", {})
            total = sum(stats.values()) if isinstance(stats, dict) else 0
            score = item["score"]
            
            justification_lines.append(
                f"{i}. **{name}** ({types}) - Total Stats: {total}, Score: {score}"
            )
        
        justification_lines.append("\n### Justification")
        justification_lines.append("- Team selected based on highest combined stats and type coverage")
        if opponent_types:
            justification_lines.append(f"- Prioritized Pokémon without {', '.join(opponent_types)} typing for better matchup")
        justification_lines.append("- Bonus given to dual-type Pokémon for versatility")
        
        # Calculate team strength for the recommended team
        team_analysis = await self.calculate_team_strength(team_names)
        
        return {
            "recommended_team": team_names,
            "opponent_types": opponent_types,
            "justification": "\n".join(justification_lines),
            "team_analysis": team_analysis
        }

    async def compare_generations(
        self, 
        generation_ids: List[str] | None = None,
        criteria: str = "variety"
    ) -> Dict[str, Any]:
        """Compare Pokémon generations by various criteria.
        
        Evaluates generations based on:
        - Type variety
        - Average stats
        - Number of Pokémon
        - Special characteristics
        
        Args:
            generation_ids: List of generation IDs (e.g., ["1", "2", "3"]). 
                           If None, compares first 3 generations
            criteria: Comparison criteria ("variety", "stats", "count")
            
        Returns:
            Comparison results with justification and winner
        """
        generation_ids = generation_ids or ["1", "2", "3"]
        
        if not generation_ids:
            raise ValidationError(
                message="At least one generation must be specified",
                field="generation_ids",
                value=[]
            )
        
        valid_criteria = ["variety", "stats", "count"]
        if criteria not in valid_criteria:
            raise ValidationError(
                message=f"Criteria must be one of: {', '.join(valid_criteria)}",
                field="criteria",
                value=criteria
            )
        
        generation_data = []
        
        for gen_id in generation_ids:
            try:
                gen_info = await self._repository.get_generation(gen_id)
                
                # Extract Pokémon species from generation
                species_list = gen_info.get("pokemon_species", [])
                pokemon_names = [
                    s.get("name") for s in species_list[:50]  # Limit for performance
                    if isinstance(s, dict) and s.get("name")
                ]
                
                # Fetch summaries for type and stat analysis
                summaries = []
                all_types = []
                total_stats = defaultdict(int)
                
                for name in pokemon_names[:30]:  # Further limit for API calls
                    try:
                        summary = await self.get_pokemon_summary(name)
                        summaries.append(summary)
                        all_types.extend(summary.get("types", []))
                        
                        stats = summary.get("stats", {})
                        for stat_name, value in stats.items():
                            if isinstance(value, (int, float)):
                                total_stats[stat_name] += value
                    except Exception:
                        continue
                
                # Calculate metrics
                unique_types = set(all_types)
                type_diversity = len(unique_types)
                
                avg_stats = {
                    k: round(v / len(summaries), 2) if summaries else 0 
                    for k, v in total_stats.items()
                }
                avg_total = sum(avg_stats.values()) if avg_stats else 0
                
                generation_data.append({
                    "generation": gen_id,
                    "name": gen_info.get("name", f"generation-{gen_id}"),
                    "total_pokemon": len(species_list),
                    "analyzed_pokemon": len(summaries),
                    "type_diversity": type_diversity,
                    "unique_types": list(unique_types),
                    "average_stats": avg_stats,
                    "average_total_stats": round(avg_total, 2),
                    "main_region": gen_info.get("main_region", {}).get("name", "unknown")
                })
                
            except Exception as e:
                continue
        
        if not generation_data:
            raise ValidationError(
                message="No generation data could be retrieved",
                field="generation_ids",
                value=generation_ids
            )
        
        # Determine winner based on criteria
        winner = None
        if criteria == "variety":
            winner = max(generation_data, key=lambda x: x["type_diversity"])
            score_key = "type_diversity"
        elif criteria == "stats":
            winner = max(generation_data, key=lambda x: x["average_total_stats"])
            score_key = "average_total_stats"
        elif criteria == "count":
            winner = max(generation_data, key=lambda x: x["total_pokemon"])
            score_key = "total_pokemon"
        
        # Generate comparison table and justification
        markdown_lines = [f"# Generation Comparison (Criteria: {criteria.title()})\n"]
        
        markdown_lines.append("## Summary Table\n")
        markdown_lines.append("| Generation | Region | Total Pokémon | Type Diversity | Avg Total Stats |")
        markdown_lines.append("|------------|--------|---------------|----------------|-----------------|")
        
        for gen in generation_data:
            gen_name = gen["name"].replace("generation-", "Gen ")
            markdown_lines.append(
                f"| {gen_name} | {gen['main_region']} | {gen['total_pokemon']} | "
                f"{gen['type_diversity']} types | {gen['average_total_stats']} |"
            )
        
        markdown_lines.append(f"\n## Winner: {winner['name'].replace('generation-', 'Generation ')}\n")
        
        markdown_lines.append("### Justification\n")
        
        if criteria == "variety":
            markdown_lines.append(
                f"- **{winner['name']}** has the highest type diversity with "
                f"**{winner['type_diversity']} unique types**: {', '.join(sorted(winner['unique_types']))}"
            )
            markdown_lines.append(
                "- Greater type diversity provides better coverage and strategic options in battles"
            )
        elif criteria == "stats":
            markdown_lines.append(
                f"- **{winner['name']}** has the highest average total stats: "
                f"**{winner['average_total_stats']}**"
            )
            markdown_lines.append(
                "- Higher average stats indicate stronger Pokémon overall"
            )
            top_stats = sorted(winner["average_stats"].items(), key=lambda x: x[1], reverse=True)[:3]
            markdown_lines.append(
                f"- Top stats: {', '.join(f'{k.title()}: {v}' for k, v in top_stats)}"
            )
        elif criteria == "count":
            markdown_lines.append(
                f"- **{winner['name']}** introduced the most Pokémon: "
                f"**{winner['total_pokemon']} species**"
            )
            markdown_lines.append(
                "- More Pokémon means more variety and team-building options"
            )
        
        markdown_lines.append("\n### All Generations Analysis\n")
        for i, gen in enumerate(generation_data, 1):
            gen_name = gen["name"].replace("generation-", "Generation ")
            markdown_lines.append(f"\n**{i}. {gen_name}** ({gen['main_region']})")
            markdown_lines.append(f"- Total Pokémon: {gen['total_pokemon']}")
            markdown_lines.append(f"- Type Diversity: {gen['type_diversity']} types")
            markdown_lines.append(f"- Average Total Stats: {gen['average_total_stats']}")
            
            if gen["unique_types"]:
                markdown_lines.append(f"- Types: {', '.join(sorted(gen['unique_types']))}")
        
        return {
            "criteria": criteria,
            "generations_compared": [g["generation"] for g in generation_data],
            "winner": winner["generation"],
            "winner_name": winner["name"],
            "winner_score": winner[score_key],
            "comparison_data": generation_data,
            "markdown": "\n".join(markdown_lines)
        }


    async def analyze_personality_from_starters(
        self,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze personality based on Pokemon starter preferences and statistics.
        
        This function analyzes all official starter Pokemon across generations and
        maps their stat distributions to personality traits based on user preferences.
        
        Personality Mapping:
        - High HP -> Resilient, Patient, Enduring
        - High Attack -> Assertive, Direct, Competitive
        - High Defense -> Cautious, Protective, Strategic
        - High Sp. Attack -> Creative, Intellectual, Innovative
        - High Sp. Defense -> Composed, Stable, Thoughtful
        - High Speed -> Energetic, Adaptable, Quick-thinking
        
        Args:
            preferences: Dictionary with user preferences:
                - battle_style: "aggressive", "defensive", "balanced", "tactical"
                - preferred_stat: "hp", "attack", "defense", "special-attack", "special-defense", "speed"
                - element_preference: "fire", "water", "grass", "any"
                
        Returns:
            Personality analysis with matched starter and traits
        """
        if not preferences:
            raise ValidationError(
                message="Preferences dictionary cannot be empty",
                field="preferences",
                value=preferences
            )
        
        # Official starter Pokemon from all generations
        all_starters = [
            # Gen 1
            "bulbasaur", "charmander", "squirtle",
            # Gen 2
            "chikorita", "cyndaquil", "totodile",
            # Gen 3
            "treecko", "torchic", "mudkip",
            # Gen 4
            "turtwig", "chimchar", "piplup",
            # Gen 5
            "snivy", "tepig", "oshawott",
            # Gen 6
            "chespin", "fennekin", "froakie",
            # Gen 7
            "rowlet", "litten", "popplio",
            # Gen 8
            "grookey", "scorbunny", "sobble",
            # Gen 9
            "sprigatito", "fuecoco", "quaxly"
        ]
        
        # Fetch all starter data
        starter_data = []
        for starter_name in all_starters:
            try:
                summary = await self.get_pokemon_summary(starter_name)
                starter_data.append(summary)
            except Exception:
                continue
        
        if not starter_data:
            raise ValidationError(
                message="Unable to fetch starter Pokemon data",
                field="starters",
                value=[]
            )
        
        # Filter by element preference if specified
        element_pref = preferences.get("element_preference", "any")
        if element_pref != "any":
            starter_data = [
                s for s in starter_data 
                if element_pref in s.get("types", [])
            ]
        
        # Score starters based on preferences
        battle_style = preferences.get("battle_style", "balanced")
        preferred_stat = preferences.get("preferred_stat")
        
        scored_starters = []
        for starter in starter_data:
            stats = starter.get("stats", {})
            score = 0
            
            # Battle style scoring
            if battle_style == "aggressive":
                score += stats.get("attack", 0) * 2
                score += stats.get("special-attack", 0) * 2
                score += stats.get("speed", 0) * 1.5
            elif battle_style == "defensive":
                score += stats.get("hp", 0) * 2
                score += stats.get("defense", 0) * 2
                score += stats.get("special-defense", 0) * 2
            elif battle_style == "tactical":
                score += stats.get("special-attack", 0) * 2
                score += stats.get("special-defense", 0) * 1.5
                score += stats.get("speed", 0) * 1.5
            else:  # balanced
                score += sum(stats.values()) if stats else 0
            
            # Preferred stat bonus
            if preferred_stat and preferred_stat in stats:
                score += stats[preferred_stat] * 3
            
            scored_starters.append({
                "starter": starter,
                "score": score
            })
        
        # Select best match
        scored_starters.sort(key=lambda x: x["score"], reverse=True)
        best_match = scored_starters[0]["starter"] if scored_starters else None
        
        if not best_match:
            raise ValidationError(
                message="No suitable starter found for preferences",
                field="preferences",
                value=preferences
            )
        
        # Analyze personality traits based on stats
        stats = best_match.get("stats", {})
        
        # Define stat-to-trait mappings
        trait_mappings = {
            "hp": {
                "high": ["Resilient", "Patient", "Enduring", "Steadfast"],
                "description": "You have great stamina and can handle prolonged challenges"
            },
            "attack": {
                "high": ["Assertive", "Direct", "Competitive", "Bold"],
                "description": "You tackle problems head-on with confidence and determination"
            },
            "defense": {
                "high": ["Cautious", "Protective", "Strategic", "Reliable"],
                "description": "You think before acting and protect what matters to you"
            },
            "special-attack": {
                "high": ["Creative", "Intellectual", "Innovative", "Visionary"],
                "description": "You approach challenges with unique and creative solutions"
            },
            "special-defense": {
                "high": ["Composed", "Stable", "Thoughtful", "Wise"],
                "description": "You remain calm under pressure and think things through"
            },
            "speed": {
                "high": ["Energetic", "Adaptable", "Quick-thinking", "Dynamic"],
                "description": "You adapt quickly to change and think on your feet"
            }
        }
        
        # Identify top 3 stats
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        top_stats = sorted_stats[:3]
        
        # Generate personality traits
        personality_traits = []
        trait_descriptions = []
        
        for stat_name, stat_value in top_stats:
            if stat_name in trait_mappings:
                mapping = trait_mappings[stat_name]
                personality_traits.extend(mapping["high"][:2])  # Take top 2 traits per stat
                trait_descriptions.append({
                    "stat": stat_name.replace("-", " ").title(),
                    "value": stat_value,
                    "traits": mapping["high"],
                    "description": mapping["description"]
                })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_traits = []
        for trait in personality_traits:
            if trait not in seen:
                seen.add(trait)
                unique_traits.append(trait)
        
        # Generate personality summary
        name = best_match.get("name", "unknown").title()
        types = "/".join(t.title() for t in best_match.get("types", []))
        
        summary_lines = [f"# Your Pokemon Personality: {name}\n"]
        summary_lines.append(f"**Type**: {types}")
        summary_lines.append(f"**Generation**: {self._get_generation_from_id(best_match.get('id', 0))}\n")
        
        summary_lines.append("## Your Personality Traits\n")
        summary_lines.append(f"**Core Traits**: {', '.join(unique_traits[:6])}\n")
        
        summary_lines.append("## Trait Analysis\n")
        summary_lines.append("Your personality is shaped by these dominant characteristics:\n")
        
        for i, trait_info in enumerate(trait_descriptions, 1):
            summary_lines.append(f"### {i}. {trait_info['stat']} (Value: {trait_info['value']})")
            summary_lines.append(f"- **Traits**: {', '.join(trait_info['traits'])}")
            summary_lines.append(f"- {trait_info['description']}\n")
        
        summary_lines.append("## Why This Pokemon Matches You\n")
        
        # Generate matching explanation
        if battle_style == "aggressive":
            summary_lines.append(
                f"- Your aggressive battle style aligns with {name}'s offensive capabilities"
            )
        elif battle_style == "defensive":
            summary_lines.append(
                f"- Your defensive approach matches {name}'s resilient nature"
            )
        elif battle_style == "tactical":
            summary_lines.append(
                f"- Your tactical mindset resonates with {name}'s strategic strengths"
            )
        else:
            summary_lines.append(
                f"- Your balanced approach is reflected in {name}'s well-rounded stats"
            )
        
        if element_pref != "any":
            summary_lines.append(
                f"- Your preference for {element_pref.title()}-type aligns with {name}'s elemental nature"
            )
        
        if preferred_stat:
            stat_display = preferred_stat.replace("-", " ").title()
            summary_lines.append(
                f"- You prioritize {stat_display}, which is one of {name}'s strongest attributes"
            )
        
        summary_lines.append(f"\n## Top 3 Alternative Matches\n")
        for i, item in enumerate(scored_starters[1:4], 1):
            alt_starter = item["starter"]
            alt_name = alt_starter.get("name", "unknown").title()
            alt_types = "/".join(t.title() for t in alt_starter.get("types", []))
            alt_score = round(item["score"], 2)
            summary_lines.append(f"{i}. **{alt_name}** ({alt_types}) - Score: {alt_score}")
        
        return {
            "matched_starter": best_match.get("name"),
            "starter_details": best_match,
            "personality_traits": unique_traits[:6],
            "trait_analysis": trait_descriptions,
            "preferences_used": preferences,
            "match_score": round(scored_starters[0]["score"], 2),
            "alternative_matches": [
                {
                    "name": s["starter"].get("name"),
                    "score": round(s["score"], 2)
                }
                for s in scored_starters[1:4]
            ],
            "summary": "\n".join(summary_lines)
        }
    
    def _get_generation_from_id(self, pokemon_id: int) -> str:
        """Determine generation from Pokemon ID."""
        if pokemon_id <= 151:
            return "I (Kanto)"
        elif pokemon_id <= 251:
            return "II (Johto)"
        elif pokemon_id <= 386:
            return "III (Hoenn)"
        elif pokemon_id <= 493:
            return "IV (Sinnoh)"
        elif pokemon_id <= 649:
            return "V (Unova)"
        elif pokemon_id <= 721:
            return "VI (Kalos)"
        elif pokemon_id <= 809:
            return "VII (Alola)"
        elif pokemon_id <= 905:
            return "VIII (Galar)"
        else:
            return "IX (Paldea)"


def create_pokemon_service(repository: IPokemonRepository) -> IPokemonService:
    """Factory function to create service instances."""
    return PokemonService(repository)
