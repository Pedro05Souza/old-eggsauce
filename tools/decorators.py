"""
This module contains the decorators used in the bot. The  pricing decorator is the core of the bot's economy system.
The listener_checks decorator is used to check if the listener can happen given guild active modules.
The before_loop_decorator is used to decorate the before_loop function in the task.
"""
from typing import Any, Callable
from discord.ext import commands
from discord.ext.commands import Context
from tools.points_core import get_config_data, retrieve_user_data, validate_command, get_points_commands_submodules, verify_farm_command, verify_and_handle_points


__all__ = ['pricing', 'before_loop_decorator']


def pricing(cache_copy: bool = False) -> Callable[[Callable [..., Any]], Callable[..., Any]]:
    """
    Decorator predicate for the points commands. This is the core of the bot's interactive system.
    Always use this when making a points command.

    Args:
        cache_copy (bool): Whether to use the cache copy or reference. 
        If false, the cache reference will be used, meaing it can change
        states during runtime. If true, the cache copy will be used, meaning
        the cache data will be frozen at the time of the command invocation.

    Returns:
        dict
    """
    async def predicate(ctx: Context) -> bool:
        config_data = await get_config_data(ctx)

        if not config_data:
            return False
        
        if not await validate_command(ctx):
            return False
        
        data = await retrieve_user_data(ctx, cache_copy)

        if not data:
            return False
        
        if not await get_points_commands_submodules(ctx, config_data):
            return False
        
        if not await verify_farm_command(ctx, data):
            return False
        
        return await verify_and_handle_points(ctx, ctx.command.name, data["user_data"], config_data, data)
    
    return commands.check(predicate)

def before_loop_decorator(task_func) -> Callable[..., Any]:
    """
    Decorator for the before_loop function in the task.

    Args:
        task_func: The task function.

    Returns:
        None
    """
    async def before_loop(self):
        await self.bot.wait_until_ready()
    task_func.before_loop = before_loop
    return task_func